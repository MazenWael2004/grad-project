from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import logging
import json

import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from AI_Agents.Travel_planner.agent import root_agent
    from AI_Agents.Travel_planner.json_utils import extract_json_from_response
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
except ImportError as e:
    logging.error(f"Failed to import Agent: {e}")
    root_agent = None
    extract_json_from_response = None

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_itinerary(request):
    if not root_agent:
        return Response({"error": "Travel Agent not initialized"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user_preferences = request.data
    
    query = f"""
    Plan a trip with the following preferences:
    Origin: {user_preferences.get('origin', 'Cairo')}
    Destination: {user_preferences.get('governorateId', 'Unknown')}
    Dates: {user_preferences.get('startTripDate')} to {user_preferences.get('endTripDate')}
    Budget: {user_preferences.get('budgetId', 'Unknown')}
    Party: {user_preferences.get('partyId', 'Unknown')}
    Interests: {user_preferences.get('interests', [])}
    """
    
    print(f"DEBUG: Generating itinerary for: {user_preferences}")
    
    
    import asyncio
    
    async def run_agent():
        print("DEBUG: Inside run_agent, starting session...")
        response_text = ""
        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name="travel_planner_app", session_service=session_service)
        session_id = f"session_{user_preferences.get('userId', 'guest')}"
        await session_service.create_session(app_name="travel_planner_app", user_id="user", session_id=session_id)
        
        print(f"DEBUG: Session created. Running agent with query...")
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)])
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        # print(f"DEBUG: Received part: {part.text[:50]}...")
                        response_text += part.text
        print("DEBUG: Agent execution finished.")
        return response_text

    try:
        
        print("DEBUG: Calling asyncio.run(run_agent())")
        response_json_str = asyncio.run(run_agent())
        print(f"DEBUG: asyncio.run returned. Length of response: {len(response_json_str)}")
        print(f"DEBUG: Agent Response: {response_json_str}")
        
        
        print("DEBUG: Extracting JSON from response...")
        data = extract_json_from_response(response_json_str)
        if data is None:
            print(f"ERROR: Could not extract JSON. Raw response: {response_json_str[:500]}")
            return Response(
                {"error": "Agent returned a response that could not be parsed as JSON."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        print("DEBUG: JSON extracted successfully. Returning response.")
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR in generate_itinerary: {e}")
        import traceback
        traceback.print_exc()
        logging.error(f"Error generating itinerary: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
