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
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
    print("✅ Travel agent loaded successfully.")
except ImportError as e:
    logging.error(f"Failed to import Agent: {e}")
    root_agent = None
    extract_json_from_response = None

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

    destination     = GOVERNORATES.get(gov_id,    f"Egyptian governorate (id={gov_id})")
    budget_label    = BUDGETS.get(budget_id,       f"Budget level {budget_id}")
    party_label     = PARTIES.get(party_id,        f"Party type {party_id}")
    interest_labels = [INTERESTS[i] for i in interest_ids if i in INTERESTS]
    interests_str   = ", ".join(interest_labels) if interest_labels else "General sightseeing"

    query = f"""
Plan a trip with the following preferences:
- Origin: Cairo, Egypt
- Destination: {destination}, Egypt
- Dates: {user_preferences.get('startTripDate', 'Not specified')} to {user_preferences.get('endTripDate', 'Not specified')}
- Budget level: {budget_label}
- Travelers: {party_label}
- Interests: {interests_str}

Please return the full itinerary as a JSON object matching the TripPlan schema,
wrapped in a ```json ... ``` code block.
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
        response_text = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        print("DEBUG: Agent finished.")
        return response_text

    try:
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        print("DEBUG: Calling asyncio.run(run_agent())")
        response_json_str = asyncio.run(asyncio.wait_for(run_agent(), timeout=300) )
        print(f"DEBUG: Raw agent response (first 500 chars):\n{response_json_str[:500]}")

        data = extract_json(response_json_str)

        if data is None:
            print(f"ERROR: Could not extract JSON. Full response:\n{response_json_str}")
            return Response(
                {
                    "error": "Agent returned a response but it could not be parsed as JSON.",
                    "raw_response": response_json_str[:2000]
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