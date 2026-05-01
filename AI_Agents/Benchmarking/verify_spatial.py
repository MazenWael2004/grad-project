"""
verify_spatial.py — Spatial Coherence Verification for Travel Itineraries

This script checks whether a generated travel itinerary makes spatial sense by:
1. Extracting landmarks and their coordinates from the TripPlan
2. Matching itinerary activities to landmarks by name
3. Computing distances between consecutive activities using the Haversine formula
4. Estimating travel times and flagging unrealistic transitions
5. Optionally running the full judge agent for combined constraint + spatial evaluation

Usage:
    python verify_spatial.py                   # Run with built-in test cases
    python verify_spatial.py --file plan.json  # Verify a specific plan file
"""

import sys
import os
import json
import argparse
import asyncio
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(env_path)

from AI_Agents.Travel_planner.tools import calculate_distance_tool

# ─── Configuration ───────────────────────────────────────────────────────────

URBAN_SPEED_KMH = 30       # Average urban travel speed (km/h)
INTERCITY_SPEED_KMH = 80   # Average intercity travel speed (km/h)
MAX_URBAN_DISTANCE_KM = 50 # Max km between consecutive activities before flagging
MAX_TRAVEL_TIME_HOURS = 2  # Max acceptable travel time between back-to-back activities


# ─── Core Spatial Analysis ───────────────────────────────────────────────────

def build_landmark_index(landmarks: list[dict]) -> dict:
    """
    Build a lookup dictionary mapping landmark titles (lowercased) to their coordinates.
    
    Args:
        landmarks: List of landmark dicts with 'title' and 'coordinate' keys.
    
    Returns:
        Dict mapping lowercase title -> (latitude, longitude)
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


def match_activity_to_landmark(activity_title: str, landmark_index: dict):
    """
    Try to match an activity title to a landmark's coordinates.
    Uses substring matching as a fallback if exact match fails.
    
    Args:
        activity_title: The activity/place name from the itinerary.
        landmark_index: Dict mapping lowercase landmark title -> (lat, lon).
    
    Returns:
        (lat, lon) tuple if matched, None otherwise.
    """
    title_lower = activity_title.lower().strip()
    
    # Exact match
    if title_lower in landmark_index:
        return landmark_index[title_lower]
    
    # Substring match: check if any landmark name is contained in activity title or vice versa
    for lm_title, coords in landmark_index.items():
        if lm_title in title_lower or title_lower in lm_title:
            return coords
    
    return None


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
    
    Args:
        day_plan: A day plan dict with 'day' and 'activities' keys.
        landmark_index: Dict mapping landmark title -> (lat, lon).
    
    Returns:
        Dict with 'day', 'transitions', 'issues', and 'unmatched_activities'.
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
        coords = match_activity_to_landmark(title, landmark_index)
        if coords:
            resolved.append({"title": title, "lat": coords[0], "lon": coords[1]})
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
            "to": b["title"],
            "distance_km": round(distance_km, 2),
            "estimated_travel_time_hrs": round(travel_time_hrs, 2),
        }
        transitions.append(transition)
        
        # Flag issues
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
    
    return {
        "day": day_label,
        "transitions": transitions,
        "issues": issues,
        "unmatched_activities": unmatched,
    }


def analyze_spatial_coherence(trip_plan: dict) -> dict:
    """
    Perform a full spatial coherence analysis on a TripPlan.
    
    Args:
        trip_plan: A TripPlan dict with 'landmarks' and 'itinerary' keys.
    
    Returns:
        Dict with overall analysis results including per-day breakdowns,
        all spatial issues, a coherence score, and unmatched activities.
    """
    landmarks = trip_plan.get("landmarks", [])
    itinerary = trip_plan.get("itinerary", [])
    
    if not landmarks:
        return {
            "spatial_score": 0.0,
            "spatial_issues": ["No landmarks found in the plan - cannot verify spatial coherence."],
            "per_day": [],
            "unmatched_activities": [],
            "total_transitions": 0,
            "flagged_transitions": 0,
        }
    
    landmark_index = build_landmark_index(landmarks)
    
    all_issues = []
    all_unmatched = []
    per_day_results = []
    total_transitions = 0
    flagged_transitions = 0
    
    for day_plan in itinerary:
        day_result = analyze_day_spatial(day_plan, landmark_index)
        per_day_results.append(day_result)
        all_issues.extend(day_result["issues"])
        all_unmatched.extend(day_result["unmatched_activities"])
        total_transitions += len(day_result["transitions"])
        flagged_transitions += len(day_result["issues"])
    
    # Compute spatial coherence score
    if total_transitions == 0:
        spatial_score = 1.0  # No transitions to evaluate (single-activity days)
    else:
        spatial_score = round(1.0 - (flagged_transitions / total_transitions), 2)
        spatial_score = max(0.0, spatial_score)
    
    return {
        "spatial_score": spatial_score,
        "spatial_issues": all_issues,
        "per_day": per_day_results,
        "unmatched_activities": list(set(all_unmatched)),
        "total_transitions": total_transitions,
        "flagged_transitions": flagged_transitions,
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


# ─── Report Formatting ──────────────────────────────────────────────────────

def print_spatial_report(analysis: dict, plan_name: str = "Plan"):
    """Print a formatted spatial coherence report."""
    print(f"\n{'='*70}")
    print(f"  SPATIAL COHERENCE REPORT -- {plan_name}")
    print(f"{'='*70}")
    
    score = analysis["spatial_score"]
    score_bar = "#" * int(score * 20) + "-" * (20 - int(score * 20))
    print(f"\n  Score: [{score_bar}] {score:.0%}")
    print(f"  Transitions analyzed: {analysis['total_transitions']}")
    print(f"  Issues flagged: {analysis['flagged_transitions']}")
    
    if analysis["unmatched_activities"]:
        print(f"\n  [!] Unmatched activities (no coordinates found):")
        for name in analysis["unmatched_activities"]:
            print(f"    - {name}")
    
    for day in analysis["per_day"]:
        print(f"\n  -- {day['day']} --")
        if not day["transitions"]:
            print("    No transitions to evaluate (0-1 located activities)")
            continue
        for t in day["transitions"]:
            status = "[OK]" if t["distance_km"] <= MAX_URBAN_DISTANCE_KM else "[!!]"
            print(
                f"    {status} {t['from']:<25s} -> {t['to']:<25s}  "
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
    
    # Test 1: Good plan (all Cairo, close together)
    print("\n>> TEST 1: Good Plan (all Cairo activities, close proximity)")
    good_analysis = analyze_spatial_coherence(GOOD_PLAN)
    print_spatial_report(good_analysis, "Cairo Explorer (Good)")
    
    if good_analysis["spatial_score"] >= 0.7:
        print("  [PASS] TEST 1 PASSED - Good plan scored well spatially.\n")
    else:
        print("  [FAIL] TEST 1 FAILED - Good plan unexpectedly scored poorly.\n")
    
    # Test 2: Bad plan (Cairo + Luxor same day)
    print(">> TEST 2: Bad Plan (Cairo -> Luxor in same day)")
    bad_analysis = analyze_spatial_coherence(BAD_PLAN)
    print_spatial_report(bad_analysis, "Impossible Egypt Tour (Bad)")
    
    if bad_analysis["spatial_issues"] and bad_analysis["spatial_score"] < 0.7:
        print("  [PASS] TEST 2 PASSED - Bad plan correctly flagged spatial issues.\n")
    else:
        print("  [FAIL] TEST 2 FAILED - Bad plan was not flagged properly.\n")
    
    return good_analysis, bad_analysis


def verify_plan_file(filepath: str):
    """Load and verify a TripPlan JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    analysis = analyze_spatial_coherence(plan)
    print_spatial_report(analysis, os.path.basename(filepath))
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
