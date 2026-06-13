"""
verify_spatial.py -- Spatial Coherence Verification for Travel Itineraries

Checks whether a generated travel itinerary makes spatial sense by:
1. Extracting coordinates from landmarks, local data (restaurants/hotels/places)
2. Matching itinerary activities to coordinates using fuzzy token matching
3. Computing distances between consecutive activities (Haversine)
4. Estimating travel times and flagging unrealistic transitions
5. Detecting routing inefficiency (zigzagging)
6. Penalizing low coordinate coverage in the score

Usage:
    python verify_spatial.py                   # Run with built-in test cases
    python verify_spatial.py --file plan.json  # Verify a specific plan file
"""

import sys
import os
import json
import argparse
import asyncio
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(env_path)

from AI_Agents.Travel_planner.tools import calculate_distance_tool
from AI_Agents.Benchmarking.benchmark_logger import log_result

# -- Configuration ------------------------------------------------------------

URBAN_SPEED_KMH = 30       # Average urban travel speed (km/h)
INTERCITY_SPEED_KMH = 80   # Average intercity travel speed (km/h)
MAX_URBAN_DISTANCE_KM = 50 # Max km between consecutive activities before flagging
MAX_TRAVEL_TIME_HOURS = 2  # Max acceptable travel time between back-to-back activities
COVERAGE_PENALTY_THRESHOLD = 0.5  # If less than 50% of activities are matched, penalize score
ZIGZAG_RETURN_THRESHOLD_KM = 5    # If route returns within 5km of a previous point, flag zigzag

# -- Load local data as fallback coordinate sources ----------------------------

_data_dir = os.path.join(os.path.dirname(__file__), '..', 'Travel_planner', 'data')

def _load_json(filename):
    path = os.path.join(_data_dir, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

_local_restaurants = _load_json("restaurants.json")
_local_hotels = _load_json("hotels.json")
_local_places = _load_json("egypt_places.json")


def build_local_coords_index() -> dict:
    """
    Build a coordinate lookup from all local data files (restaurants, hotels, places).
    Returns dict mapping lowercase name -> (latitude, longitude).
    """
    index = {}
    for r in _local_restaurants:
        name = r.get("name", "").lower().strip()
        lat, lon = r.get("latitude"), r.get("longitude")
        if name and lat is not None and lon is not None:
            index[name] = (lat, lon)
    for h in _local_hotels:
        name = h.get("name", "").lower().strip()
        lat, lon = h.get("latitude"), h.get("longitude")
        if name and lat is not None and lon is not None:
            index[name] = (lat, lon)
    for p in _local_places:
        name = p.get("name", "").lower().strip()
        lat, lon = p.get("latitude"), p.get("longitude")
        if name and lat is not None and lon is not None:
            index[name] = (lat, lon)
    return index

_local_coords = build_local_coords_index()


# -- Core Spatial Analysis -----------------------------------------------------

# Common prefixes to strip when matching activity titles to location names
_STRIP_PREFIXES = [
    "lunch at", "dinner at", "breakfast at", "visit", "explore",
    "tour of", "tour", "sunset at", "morning at", "evening at",
    "farewell dinner at", "arrive at", "check in at", "check-in at",
]


def build_landmark_index(landmarks: list[dict]) -> dict:
    """
    Build a lookup dictionary mapping landmark titles (lowercased) to their coordinates.
    """
    index = {}
    for lm in landmarks:
        title = lm.get("title", "").lower().strip()
        coord = lm.get("coordinate", {})
        lat = coord.get("latitude")
        lon = coord.get("longitude")
        if title and lat is not None and lon is not None:
            index[title] = (lat, lon)
    return index


def _strip_activity_prefix(title: str) -> str:
    """Strip common prefixes like 'Lunch at', 'Dinner at' from activity titles."""
    lower = title.lower().strip()
    for prefix in sorted(_STRIP_PREFIXES, key=len, reverse=True):
        if lower.startswith(prefix):
            stripped = lower[len(prefix):].strip()
            if stripped:
                return stripped
    return lower


def _token_match(name_a: str, name_b: str) -> bool:
    """
    Check if two names share significant word tokens.
    Returns True if all tokens of the shorter name appear in the longer one.
    E.g., 'abou tarek' matches 'koshary abou tarek' and 'lunch at abou tarek'.
    """
    tokens_a = set(name_a.lower().split())
    tokens_b = set(name_b.lower().split())
    # Remove trivial words
    trivial = {"the", "a", "an", "at", "in", "of", "and", "&", "-", "to", "for"}
    tokens_a -= trivial
    tokens_b -= trivial
    if not tokens_a or not tokens_b:
        return False
    smaller, larger = (tokens_a, tokens_b) if len(tokens_a) <= len(tokens_b) else (tokens_b, tokens_a)
    return smaller.issubset(larger)


def match_activity_to_coords(activity_title: str, landmark_index: dict):
    """
    Try to match an activity title to coordinates using a 3-tier strategy:
      1. Exact/substring match against plan landmarks
      2. Token-based fuzzy match against plan landmarks
      3. Fuzzy match against local data (restaurants, hotels, places)

    Args:
        activity_title: The activity/place name from the itinerary.
        landmark_index: Dict mapping lowercase landmark title -> (lat, lon).

    Returns:
        (lat, lon, source) tuple if matched, (None, None, None) otherwise.
        source is 'landmark', 'local_data', or None.
    """
    title_lower = activity_title.lower().strip()
    stripped = _strip_activity_prefix(activity_title)

    # --- Tier 1: Exact / substring match against landmarks ---
    if title_lower in landmark_index:
        return (*landmark_index[title_lower], "landmark")
    if stripped in landmark_index:
        return (*landmark_index[stripped], "landmark")
    for lm_title, coords in landmark_index.items():
        if lm_title in title_lower or title_lower in lm_title:
            return (*coords, "landmark")
        if lm_title in stripped or stripped in lm_title:
            return (*coords, "landmark")

    # --- Tier 2: Token-based fuzzy match against landmarks ---
    for lm_title, coords in landmark_index.items():
        if _token_match(stripped, lm_title):
            return (*coords, "landmark")

    # --- Tier 3: Match against local data (restaurants, hotels, places) ---
    if stripped in _local_coords:
        return (*_local_coords[stripped], "local_data")
    for local_name, coords in _local_coords.items():
        if local_name in stripped or stripped in local_name:
            return (*coords, "local_data")
    for local_name, coords in _local_coords.items():
        if _token_match(stripped, local_name):
            return (*coords, "local_data")

    return (None, None, None)


def estimate_travel_time(distance_km: float) -> float:
    """
    Estimate travel time in hours based on distance.
    Uses urban speed for short distances, intercity speed for longer ones.
    
    Args:
        distance_km: Distance between two points in kilometers.
    
    Returns:
        Estimated travel time in hours.
    """
    if distance_km <= MAX_URBAN_DISTANCE_KM:
        return distance_km / URBAN_SPEED_KMH
    else:
        return distance_km / INTERCITY_SPEED_KMH


def analyze_day_spatial(day_plan: dict, landmark_index: dict) -> dict:
    """
    Analyze the spatial coherence of a single day's activities.
    Includes distance checks, travel time estimates, and zigzag detection.
    """
    day_label = day_plan.get("day", "Unknown Day")
    activities = day_plan.get("activities", [])

    transitions = []
    issues = []
    unmatched = []

    # Resolve coordinates for each activity
    resolved = []
    for act in activities:
        title = act.get("title", "Unknown")
        lat, lon, source = match_activity_to_coords(title, landmark_index)
        if lat is not None:
            resolved.append({"title": title, "lat": lat, "lon": lon, "source": source})
        else:
            unmatched.append(title)

    # Compute distances between consecutive resolved activities
    for i in range(len(resolved) - 1):
        a = resolved[i]
        b = resolved[i + 1]

        distance_km = calculate_distance_tool(a["lat"], a["lon"], b["lat"], b["lon"])
        travel_time_hrs = estimate_travel_time(distance_km)

        transition = {
            "from": a["title"],
            "from_source": a["source"],
            "to": b["title"],
            "to_source": b["source"],
            "distance_km": round(distance_km, 2),
            "estimated_travel_time_hrs": round(travel_time_hrs, 2),
        }
        transitions.append(transition)

        # Flag distance issues
        if distance_km > MAX_URBAN_DISTANCE_KM:
            issues.append(
                f"{day_label}: {a['title']} -> {b['title']} is {distance_km:.1f} km apart "
                f"(estimated {travel_time_hrs:.1f}h travel) - likely different cities, unrealistic for same-day travel"
            )
        elif travel_time_hrs > MAX_TRAVEL_TIME_HOURS:
            issues.append(
                f"{day_label}: {a['title']} -> {b['title']} would take ~{travel_time_hrs:.1f}h "
                f"to travel ({distance_km:.1f} km) - exceeds reasonable urban travel time"
            )

    # Zigzag detection: check if route doubles back near a previous point
    for i in range(2, len(resolved)):
        current = resolved[i]
        for j in range(i - 2):  # compare with all points before the previous one
            prev = resolved[j]
            return_dist = calculate_distance_tool(
                current["lat"], current["lon"], prev["lat"], prev["lon"]
            )
            if return_dist < ZIGZAG_RETURN_THRESHOLD_KM:
                mid = resolved[i - 1]
                detour_dist = calculate_distance_tool(prev["lat"], prev["lon"], mid["lat"], mid["lon"])
                if detour_dist > ZIGZAG_RETURN_THRESHOLD_KM:
                    issues.append(
                        f"{day_label}: Route zigzags - {prev['title']} -> {mid['title']} "
                        f"({detour_dist:.1f}km away) -> {current['title']} (returns near {prev['title']})"
                    )

    return {
        "day": day_label,
        "transitions": transitions,
        "issues": issues,
        "unmatched_activities": unmatched,
        "total_activities": len(activities),
        "matched_activities": len(resolved),
    }


def analyze_spatial_coherence(trip_plan: dict) -> dict:
    """
    Perform a full spatial coherence analysis on a TripPlan.
    Uses plan landmarks + local data (restaurants/hotels/places) for coordinate lookup.
    Penalizes score when too few activities can be geocoded.
    """
    landmarks = trip_plan.get("landmarks", [])
    itinerary = trip_plan.get("itinerary", [])

    landmark_index = build_landmark_index(landmarks)

    # Even with no landmarks, we can still try local data fallback
    if not landmarks and not _local_coords:
        return {
            "spatial_score": 0.0,
            "spatial_issues": ["No landmarks and no local data - cannot verify spatial coherence."],
            "per_day": [],
            "unmatched_activities": [],
            "total_transitions": 0,
            "flagged_transitions": 0,
            "total_activities": 0,
            "matched_activities": 0,
            "coverage": 0.0,
        }

    all_issues = []
    all_unmatched = []
    per_day_results = []
    total_transitions = 0
    flagged_transitions = 0
    total_activities = 0
    matched_activities = 0

    for day_plan in itinerary:
        day_result = analyze_day_spatial(day_plan, landmark_index)
        per_day_results.append(day_result)
        all_issues.extend(day_result["issues"])
        all_unmatched.extend(day_result["unmatched_activities"])
        total_transitions += len(day_result["transitions"])
        flagged_transitions += len(day_result["issues"])
        total_activities += day_result["total_activities"]
        matched_activities += day_result["matched_activities"]

    # Coverage ratio: what fraction of activities could be geocoded
    coverage = matched_activities / total_activities if total_activities > 0 else 0.0

    # Compute spatial coherence score
    if total_transitions == 0:
        transition_score = 1.0
    else:
        transition_score = 1.0 - (flagged_transitions / total_transitions)

    # Apply coverage penalty: if less than threshold of activities are matched,
    # reduce score proportionally so a 100% score with 20% coverage becomes ~20%
    if coverage < COVERAGE_PENALTY_THRESHOLD:
        coverage_penalty = coverage / COVERAGE_PENALTY_THRESHOLD
        spatial_score = round(transition_score * coverage_penalty, 2)
        if all_unmatched:
            all_issues.append(
                f"Low coverage: only {matched_activities}/{total_activities} activities "
                f"({coverage:.0%}) could be geocoded - spatial check is unreliable"
            )
    else:
        spatial_score = round(transition_score, 2)

    spatial_score = max(0.0, min(1.0, spatial_score))

    return {
        "spatial_score": spatial_score,
        "spatial_issues": all_issues,
        "per_day": per_day_results,
        "unmatched_activities": list(set(all_unmatched)),
        "total_transitions": total_transitions,
        "flagged_transitions": flagged_transitions,
        "total_activities": total_activities,
        "matched_activities": matched_activities,
        "coverage": round(coverage, 2),
    }


# ─── Judge Agent Integration ────────────────────────────────────────────────

async def run_judge_with_spatial(query: str, plan_json: str) -> dict:
    """
    Run the full judge agent (constraint + spatial evaluation) on a plan.
    
    Args:
        query: The user's original travel query.
        plan_json: The generated TripPlan as a JSON string.
    
    Returns:
        Dict with the judge agent's evaluation result.
    """
    from AI_Agents.Benchmarking.evaluations import evaluate_plan
    return evaluate_plan(query, plan_json)


# ─── Test Cases ──────────────────────────────────────────────────────────────

GOOD_PLAN = {
    "trip_name": "Cairo Explorer",
    "trip_summary": "A 3-day trip exploring Cairo's historical landmarks.",
    "trip_dates": "Jun 1 - Jun 3, 2026",
    "travelers_type": "Couple",
    "luxury_level": "Budget",
    "landmarks": [
        {
            "id": "egyptian_museum",
            "title": "Egyptian Museum",
            "description": "World-famous museum of Egyptian antiquities.",
            "coordinate": {"latitude": 30.0478, "longitude": 31.2336},
            "color": "#F59E0B"
        },
        {
            "id": "khan_el_khalili",
            "title": "Khan El Khalili",
            "description": "Historic bazaar and souq.",
            "coordinate": {"latitude": 30.0489, "longitude": 31.2622},
            "color": "#10B981"
        },
        {
            "id": "citadel_of_saladin",
            "title": "Citadel of Saladin",
            "description": "Medieval Islamic fortification.",
            "coordinate": {"latitude": 30.0296, "longitude": 31.2600},
            "color": "#3B82F6"
        },
        {
            "id": "pyramids_of_giza",
            "title": "Pyramids of Giza",
            "description": "Ancient wonder of the world.",
            "coordinate": {"latitude": 29.9792, "longitude": 31.1342},
            "color": "#EF4444"
        },
        {
            "id": "al_azhar_mosque",
            "title": "Al-Azhar Mosque",
            "description": "Historic mosque and university.",
            "coordinate": {"latitude": 30.0456, "longitude": 31.2633},
            "color": "#8B5CF6"
        }
    ],
    "itinerary": [
        {
            "day": "Day 1",
            "activities": [
                {"time": "09:00 AM - 11:00 AM", "title": "Egyptian Museum", "description": "Visit the museum.", "cost": "EGP 550", "rating": 4.5, "reviews_count": 1200},
                {"time": "12:00 PM - 02:00 PM", "title": "Khan El Khalili", "description": "Explore the bazaar.", "cost": "EGP 0", "rating": 4.6, "reviews_count": 900},
                {"time": "03:00 PM - 05:00 PM", "title": "Al-Azhar Mosque", "description": "Visit the mosque.", "cost": "EGP 0", "rating": 4.4, "reviews_count": 600}
            ]
        },
        {
            "day": "Day 2",
            "activities": [
                {"time": "08:00 AM - 11:00 AM", "title": "Pyramids of Giza", "description": "Explore the pyramids.", "cost": "EGP 700", "rating": 4.9, "reviews_count": 5000},
                {"time": "01:00 PM - 03:00 PM", "title": "Citadel of Saladin", "description": "Tour the citadel.", "cost": "EGP 550", "rating": 4.3, "reviews_count": 800}
            ]
        }
    ],
    "budget_breakdown": [
        "Transport: EGP 500",
        "Accommodation: EGP 2000",
        "Food: EGP 1500",
        "Activities: EGP 1800",
        "Total: EGP 5800"
    ]
}

BAD_PLAN = {
    "trip_name": "Impossible Egypt Tour",
    "trip_summary": "A 1-day trip hitting Cairo and Luxor in one day.",
    "trip_dates": "Jun 1, 2026",
    "travelers_type": "Solo",
    "luxury_level": "Budget",
    "landmarks": [
        {
            "id": "egyptian_museum",
            "title": "Egyptian Museum",
            "description": "World-famous museum.",
            "coordinate": {"latitude": 30.0478, "longitude": 31.2336},
            "color": "#F59E0B"
        },
        {
            "id": "luxor_temple",
            "title": "Luxor Temple",
            "description": "Ancient temple complex.",
            "coordinate": {"latitude": 25.6997, "longitude": 32.6390},
            "color": "#EF4444"
        },
        {
            "id": "karnak_temple",
            "title": "Karnak Temple",
            "description": "Largest ancient religious site.",
            "coordinate": {"latitude": 25.7188, "longitude": 32.6573},
            "color": "#3B82F6"
        }
    ],
    "itinerary": [
        {
            "day": "Day 1",
            "activities": [
                {"time": "08:00 AM - 10:00 AM", "title": "Egyptian Museum", "description": "Visit museum.", "cost": "EGP 550", "rating": 4.5, "reviews_count": 1200},
                {"time": "12:00 PM - 02:00 PM", "title": "Luxor Temple", "description": "Visit Luxor Temple.", "cost": "EGP 400", "rating": 4.8, "reviews_count": 3000},
                {"time": "03:00 PM - 05:00 PM", "title": "Karnak Temple", "description": "Explore Karnak.", "cost": "EGP 450", "rating": 4.7, "reviews_count": 2500}
            ]
        }
    ],
    "budget_breakdown": [
        "Transport: EGP 200",
        "Activities: EGP 1400",
        "Total: EGP 1600"
    ]
}


# -- Report Formatting ---------------------------------------------------------

def print_spatial_report(analysis: dict, plan_name: str = "Plan"):
    """Print a formatted spatial coherence report."""
    print(f"\n{'='*70}")
    print(f"  SPATIAL COHERENCE REPORT -- {plan_name}")
    print(f"{'='*70}")

    score = analysis["spatial_score"]
    score_bar = "#" * int(score * 20) + "-" * (20 - int(score * 20))
    coverage = analysis.get("coverage", 0)
    matched = analysis.get("matched_activities", 0)
    total = analysis.get("total_activities", 0)

    print(f"\n  Score:    [{score_bar}] {score:.0%}")
    print(f"  Coverage: {matched}/{total} activities geocoded ({coverage:.0%})")
    print(f"  Transitions analyzed: {analysis['total_transitions']}")
    print(f"  Issues flagged: {analysis['flagged_transitions']}")

    if analysis["unmatched_activities"]:
        print(f"\n  [!] Unmatched activities (no coordinates found):")
        for name in analysis["unmatched_activities"]:
            print(f"    - {name}")

    for day in analysis["per_day"]:
        day_matched = day.get("matched_activities", 0)
        day_total = day.get("total_activities", 0)
        print(f"\n  -- {day['day']} ({day_matched}/{day_total} located) --")
        if not day["transitions"]:
            print("    No transitions to evaluate (0-1 located activities)")
            continue
        for t in day["transitions"]:
            status = "[OK]" if t["distance_km"] <= MAX_URBAN_DISTANCE_KM else "[!!]"
            # Show source labels for coordinates
            src_from = f"[{t.get('from_source', '?')}]" if t.get("from_source") else ""
            src_to = f"[{t.get('to_source', '?')}]" if t.get("to_source") else ""
            print(
                f"    {status} {t['from']:<25s}{src_from:<13s} -> "
                f"{t['to']:<25s}{src_to:<13s} "
                f"{t['distance_km']:>7.1f} km  (~{t['estimated_travel_time_hrs']:.1f}h)"
            )

    if analysis["spatial_issues"]:
        print(f"\n  [FAIL] SPATIAL ISSUES:")
        for issue in analysis["spatial_issues"]:
            print(f"    - {issue}")
    else:
        print(f"\n  [PASS] No spatial issues detected.")

    print(f"\n{'='*70}\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def run_test_cases():
    """Run built-in test cases to validate the spatial checker."""
    start_time = time.time()
    
    # Test 1: Good plan (all Cairo, close together)
    print("\n>> TEST 1: Good Plan (all Cairo activities, close proximity)")
    good_analysis = analyze_spatial_coherence(GOOD_PLAN)
    print_spatial_report(good_analysis, "Cairo Explorer (Good)")
    
    test1_passed = good_analysis["spatial_score"] >= 0.7
    if test1_passed:
        print("  [PASS] TEST 1 PASSED - Good plan scored well spatially.\n")
    else:
        print("  [FAIL] TEST 1 FAILED - Good plan unexpectedly scored poorly.\n")
    
    # Test 2: Bad plan (Cairo + Luxor same day)
    print(">> TEST 2: Bad Plan (Cairo -> Luxor in same day)")
    bad_analysis = analyze_spatial_coherence(BAD_PLAN)
    print_spatial_report(bad_analysis, "Impossible Egypt Tour (Bad)")
    
    test2_passed = bad_analysis["spatial_issues"] and bad_analysis["spatial_score"] < 0.7
    if test2_passed:
        print("  [PASS] TEST 2 PASSED - Bad plan correctly flagged spatial issues.\n")
    else:
        print("  [FAIL] TEST 2 FAILED - Bad plan was not flagged properly.\n")
    
    elapsed = round(time.time() - start_time, 2)
    log_result(
        script_name="verify_spatial",
        results={
            "mode": "test_cases",
            "test1_good_plan": {
                "passed": test1_passed,
                "spatial_score": good_analysis["spatial_score"],
                "coverage": good_analysis.get("coverage", 0),
                "flagged_transitions": good_analysis["flagged_transitions"],
                "total_transitions": good_analysis["total_transitions"],
                "issues": good_analysis["spatial_issues"],
            },
            "test2_bad_plan": {
                "passed": test2_passed,
                "spatial_score": bad_analysis["spatial_score"],
                "coverage": bad_analysis.get("coverage", 0),
                "flagged_transitions": bad_analysis["flagged_transitions"],
                "total_transitions": bad_analysis["total_transitions"],
                "issues": bad_analysis["spatial_issues"],
            },
        },
        extra={"elapsed_seconds": elapsed},
    )
    
    return good_analysis, bad_analysis


def verify_plan_file(filepath: str):
    """Load and verify a TripPlan JSON file."""
    start_time = time.time()
    with open(filepath, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    analysis = analyze_spatial_coherence(plan)
    print_spatial_report(analysis, os.path.basename(filepath))
    
    elapsed = round(time.time() - start_time, 2)
    log_result(
        script_name="verify_spatial",
        results={
            "mode": "file",
            "file": os.path.basename(filepath),
            "spatial_score": analysis["spatial_score"],
            "coverage": analysis.get("coverage", 0),
            "total_activities": analysis.get("total_activities", 0),
            "matched_activities": analysis.get("matched_activities", 0),
            "flagged_transitions": analysis["flagged_transitions"],
            "total_transitions": analysis["total_transitions"],
            "issues": analysis["spatial_issues"],
            "unmatched_activities": analysis.get("unmatched_activities", []),
        },
        extra={"elapsed_seconds": elapsed},
    )
    
    return analysis


def main():
    parser = argparse.ArgumentParser(description="Verify spatial coherence of travel itineraries.")
    parser.add_argument("--file", type=str, help="Path to a TripPlan JSON file to verify.")
    parser.add_argument("--query", type=str, help="User query to run full judge evaluation (requires --file).")
    args = parser.parse_args()
    
    if args.file:
        analysis = verify_plan_file(args.file)
        
        if args.query:
            print("\n>> Running full judge agent (constraint + spatial)...")
            with open(args.file, "r", encoding="utf-8") as f:
                plan_json = f.read()
            result = asyncio.run(run_judge_with_spatial(args.query, plan_json))
            print(f"  Judge result: {json.dumps(result, indent=2)}")
    else:
        run_test_cases()


if __name__ == "__main__":
    main()
