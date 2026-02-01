import sys
import os
import asyncio

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Travel_planner', '.env'))
load_dotenv(env_path)


load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
print("Key loaded:", bool(api_key))

if os.getenv('OPEN_ROUTER_API_KEY'):
    os.environ['OPENROUTER_API_KEY'] = os.getenv('OPEN_ROUTER_API_KEY')

from AI_Agents.Travel_planner.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

async def main():
    
    query = "Plan a 3-day trip to cairo from saudi arabia riyadh for 2 people with a budget of 1500 SAR start date 2026-06-01 and recommanded resturants and hotels"
    print(f"Query: {query}\n")
    print("-" * 50)
    
    session_service = InMemorySessionService()
    
    runner = Runner(
        agent=root_agent,
        app_name="travel_planner_app",
        session_service=session_service
    )
    
    user_id = "test_user"
    session_id = "test_session"
    
    await session_service.create_session(
        app_name="travel_planner_app",
        user_id=user_id,
        session_id=session_id
    )

    response_text = ""
    
    # Run the agent
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    ):
        # Extract text content from events
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    text_chunk = part.text
                    response_text += text_chunk
                    print(text_chunk, end="", flush=True)
                    
    print("\n" + "-" * 50)
    print("\n" + "-" * 50)
    print("Verification:")
    import json
    import re
    
    clean_text = response_text.strip()
    code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(code_block_pattern, clean_text, re.DOTALL)
    if match:
        clean_text = match.group(1).strip()
    
    try:
        data = json.loads(clean_text)
        required_keys = ["trip_summary", "itinerary", "budget_breakdown", "landmarks"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            print(f"FAILED: Missing keys in JSON: {missing}")
        else:
            print("PASSED: Output contains all required JSON keys.")
            print(f"Landmarks count: {len(data.get('landmarks', []))}")
            print(f"Itinerary days: {len(data.get('itinerary', []))}")
    except json.JSONDecodeError:
        print("FAILED: Output is not valid JSON.")

if __name__ == "__main__":
    asyncio.run(main())
