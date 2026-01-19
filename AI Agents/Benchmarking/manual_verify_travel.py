import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Travel_planner.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

async def main():
    # Load environment variables
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'judge', '.env'))
    load_dotenv(env_path)
    
    query = "Plan a 3-day trip to Paris from London for 2 people with a budget of 1500 USD start date 2024-06-01"
    print(f"Query: {query}\n")
    print("-" * 50)
    
    # Initialize session service
    session_service = InMemorySessionService()
    
    # Initialize runner
    runner = Runner(
        agent=root_agent,
        app_name="travel_planner_app",
        session_service=session_service
    )
    
    user_id = "test_user"
    session_id = "test_session"
    
    # create session
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
    print("Verification:")
    required_keywords = ["Trip Summary", "Daily Itinerary", "Budget Breakdown"]
    missing = [k for k in required_keywords if k not in response_text]
    
    if missing:
        print(f"FAILED: Missing sections: {missing}")
    else:
        print("PASSED: Output contains all required sections.")

if __name__ == "__main__":
    asyncio.run(main())
