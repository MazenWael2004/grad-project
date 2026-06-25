from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import logging
import json
import re
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from dotenv import load_dotenv
env_path = os.path.join(BASE_DIR, 'AI_Agents', '.env')
load_dotenv(env_path)


if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "YOUR_NEW_API_KEY_HERE"

_key = os.getenv("OPENROUTER_API_KEY")
print(f"DEBUG: API Key loaded: {bool(_key)} | Starts with: {str(_key)[:15] if _key else 'NONE'}")


try:
    from AI_Agents.Travel_planner.agent import root_agent
    from AI_Agents.Travel_planner.json_utils import extract_json_from_response
    from AI_Agents.Travel_planner.clustering import get_clustered_itinerary
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
    print("[OK] Travel agent and clustering loaded successfully.")
except ImportError as e:
    logging.error(f"Failed to import Agent/Clustering: {e}")
    root_agent = None
    extract_json_from_response = None
    get_clustered_itinerary = None

GOVERNORATES = {
    1: "Cairo",
    2: "Alexandria",
    3: "Luxor",
    4: "Aswan",
    5: "Giza",
    6: "Hurghada",
    7: "Sharm El-Sheikh",
    8: "Dahab",
    9: "Marsa Matruh",
    10: "Siwa",
}

BUDGETS = {
    1: "Budget (low cost, cheap options)",
    2: "Mid-range (moderate spending)",
    3: "Luxury (high-end, premium options)",
}

PARTIES = {
    1: "Solo traveler",
    2: "Couple",
    3: "Family with children",
    4: "Group of friends",
}

INTERESTS = {
    1: "Nile Cruise",
    2: "Photographing",
    3: "Eco Tourism",
    4: "Cultural Tourism",
    5: "Camel Riding",
    6: "Festivals and Events",
    7: "Road Trips",
    8: "Food Tourism",
    9: "Backpacking",
    10: "Art Galleries",
    11: "Cultural Exploration",
}
# ── Robust JSON extractor ─────────────────────────────────────────────────────
def extract_json(text: str) -> dict | None:
    text = text.strip()

    # Strategy 1: fenced code block ```json ... ``` or ``` ... ```
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 2: balanced-brace scan
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == '{':
            try:
                obj, _ = decoder.raw_decode(text, i)
                return obj
            except json.JSONDecodeError:
                continue

    # Strategy 3: raw parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def extract_last_json(text: str) -> dict | None:
    """Find the LAST valid JSON object in the text — the final agent's output."""
    text = text.strip()
    last_obj = None

    # Strategy 1: find ALL fenced code blocks and use the last one
    fence_matches = re.findall(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    for candidate in reversed(fence_matches):
        try:
            last_obj = json.loads(candidate.strip())
            return last_obj
        except json.JSONDecodeError:
            continue

    # Strategy 2: scan all valid JSON objects and keep the last
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == '{':
            try:
                obj, _ = decoder.raw_decode(text, i)
                last_obj = obj
            except json.JSONDecodeError:
                continue

    return last_obj


# ── View ──────────────────────────────────────────────────────────────────────
def format_clusters_for_prompt(data):
    hotel = data.get("hotel")
    hotel_str = "No hotel selected"
    if hotel:
        hotel_str = (
            f"Hotel: {hotel['name']} in {hotel['city']}\n"
            f"- Price: EGP {hotel['price_per_night']}/night\n"
            f"- Rating: {hotel['rating']}/5\n"
            f"- Category: {hotel['category']}\n"
            f"- Coordinates: Latitude {hotel['latitude']}, Longitude {hotel['longitude']}"
        )

    days_str = []
    for c in data.get("clusters", []):
        day_info = [f"### Day {c['day']}:"]
        
        day_info.append("  Attractions to visit:")
        for idx, a in enumerate(c["attractions"], 1):
            day_info.append(
                f"  {idx}. {a['name']} in {a['city']}\n"
                f"     - Categories: {', '.join(a['categories'])}\n"
                f"     - Average Cost: EGP {a['average_cost']}\n"
                f"     - Visit Duration: {a['visit_duration_hours']} hours\n"
                f"     - Opening/Closing: {a['opening_time']} - {a['closing_time']}\n"
                f"     - Best Time: {a['best_time']}\n"
                f"     - Popularity: {a['popularity']}/5\n"
                f"     - Coordinates: Latitude {a['latitude']}, Longitude {a['longitude']}\n"
                f"     - Description: {a['description']}"
            )
            
        day_info.append("  Restaurants for meals:")
        for idx, r in enumerate(c["restaurants"], 1):
            day_info.append(
                f"  {idx}. {r['name']} in {r['city']}\n"
                f"     - Cuisine: {r['cuisine']}\n"
                f"     - Average Meal Cost: EGP {r['average_meal_cost']}\n"
                f"     - Rating: {r['rating']}/5\n"
                f"     - Specialty: {r['specialty']}\n"
                f"     - Coordinates: Latitude {r['latitude']}, Longitude {r['longitude']}"
            )
            
        days_str.append("\n".join(day_info))

    full_itinerary_context = (
        f"{hotel_str}\n\n"
        "Day Clusters:\n" + "\n\n".join(days_str)
    )
    return full_itinerary_context


# ── View ──────────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_itinerary(request):
    if not root_agent:
        return Response(
            {"error": "Travel Agent not initialized. Check server logs for import errors."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    user_preferences = request.data
    print(f"DEBUG: Received preferences: {user_preferences}")

    gov_id       = user_preferences.get('governorateId')
    budget_id    = user_preferences.get('budgetId')
    party_id     = user_preferences.get('partyId')
    interest_ids = user_preferences.get('interests', [])
    start_date   = user_preferences.get('startTripDate', 'Not specified')
    end_date     = user_preferences.get('endTripDate', 'Not specified')

    if get_clustered_itinerary:
        try:
            clustering_data = get_clustered_itinerary(gov_id, budget_id, interest_ids, start_date, end_date)
        except Exception as ce:
            print(f"ERROR in spatial clustering: {ce}")
            clustering_data = None
    else:
        clustering_data = None

    if not clustering_data or not clustering_data.get("clusters"):
        return Response(
            {"error": "Failed to query and cluster travel data for the specified governorate."},
            status=status.HTTP_400_BAD_REQUEST
        )

    destination     = GOVERNORATES.get(gov_id,    f"Egyptian governorate (id={gov_id})")
    budget_label    = BUDGETS.get(budget_id,       f"Budget level {budget_id}")
    party_label     = PARTIES.get(party_id,        f"Party type {party_id}")
    interest_labels = [INTERESTS[i] for i in interest_ids if i in INTERESTS]
    interests_str   = ", ".join(interest_labels) if interest_labels else "General sightseeing"

    clustered_context = format_clusters_for_prompt(clustering_data)

    query = f"""
Plan a trip with the following preferences:
- Origin: Cairo, Egypt
- Destination: {destination}, Egypt
- Dates: {start_date} to {end_date}
- Budget level: {budget_label}
- Travelers: {party_label}
- Interests: {interests_str}

Use ONLY the pre-filtered, pre-clustered database travel data provided below:

{clustered_context}

RULES:
1. Use ONLY the attractions, hotel, and restaurants listed in the day clusters above.
2. Use the EXACT prices, names, and coordinates provided. Do NOT change them.
3. Arrange the activities for each day into a logical, enjoyable timeline (morning, afternoon, evening) with times, matching the attraction opening/closing times.
4. Include check-in and meals at the specified restaurants.
5. Return the full itinerary as a JSON object matching the TripPlan schema, wrapped in a ```json ... ``` code block.
"""

    print(f"DEBUG: Agent query:\n{query}")

    import asyncio

    async def run_agent():
        print("DEBUG: Creating session...")
        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name="travel_planner_app",
            session_service=session_service
        )
        user_id    = str(user_preferences.get('userId', 'guest'))
        session_id = f"session_{user_id}"

        await session_service.create_session(
            app_name="travel_planner_app",
            user_id=user_id,
            session_id=session_id
        )

        print("DEBUG: Session created. Running agent...")
        all_response_text = ""
        last_agent_text = ""
        current_author = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
        ):
            if event.content and event.content.parts:
                author = getattr(event, 'author', '') or ''
                for part in event.content.parts:
                    if part.text:
                        text_chunk = part.text
                        all_response_text += text_chunk
                        if author != current_author:
                            current_author = author
                            last_agent_text = ""
                        last_agent_text += text_chunk

        print("DEBUG: Agent finished.")
        print(f"DEBUG: Last responding agent: {current_author}")
        return all_response_text, last_agent_text

    try:
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        print("DEBUG: Calling asyncio.run(run_agent())")
        all_response_text, last_agent_text = asyncio.run(asyncio.wait_for(run_agent(), timeout=3000))

        # ── Dump full response for debugging ──
        print("=" * 80)
        print("DEBUG: FULL RAW RESPONSE FROM ALL AGENTS:")
        print("=" * 80)
        print(all_response_text)
        print("=" * 80)
        print(f"DEBUG: Last agent text (first 1000 chars):\n{last_agent_text[:1000]}")
        print("=" * 80)
        print(f"DEBUG: Warnings from clustering: {clustering_data.get('warnings')}")

        data = extract_json(last_agent_text)
        if data is None:
            print("DEBUG: Could not extract JSON from last agent output. Trying full response...")
            data = extract_last_json(all_response_text)

        if data is None:
            print(f"ERROR: Could not extract JSON. Full response:\n{all_response_text}")
            return Response(
                {
                    "error": "Agent returned a response but it could not be parsed as JSON.",
                    "raw_response": all_response_text[:2000]
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        print("DEBUG: JSON extracted successfully. Returning response.")
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"ERROR in generate_itinerary:\n{tb}")
        logging.error(f"Error generating itinerary: {e}")
        return Response(
            {"error": str(e), "traceback": tb},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )