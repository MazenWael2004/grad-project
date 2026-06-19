import sys
import os
import time
import asyncio
import json
import re

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
from AI_Agents.Benchmarking.benchmark_logger import log_result


def extract_json(text: str) -> dict | None:
    """
    Robustly extract a JSON object from text that may contain surrounding prose
    (e.g. LLM chain-of-thought reasoning before/after the JSON block).

    Strategies tried in order:
      1. Fenced code block  ```json ... ```  or  ``` ... ```
      2. Balanced-brace scan using JSONDecoder.raw_decode() — finds the first
         '{' that starts a valid JSON object and stops exactly at the matching
         closing brace, ignoring all surrounding text.
      3. Raw parse of the entire text as-is.
    """
    text = text.strip()

    # Strategy 1: fenced code block
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # fall through

    # Strategy 2: balanced-brace scan with raw_decode
    # This correctly handles prose BEFORE and AFTER the JSON object because
    # raw_decode() stops exactly at the end of the valid JSON, unlike a greedy
    # regex that sweeps from the first '{' to the LAST '}' and captures
    # everything in between (breaking when there is reasoning text after the JSON).
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == '{':
            try:
                obj, _ = decoder.raw_decode(text, i)
                return obj
            except json.JSONDecodeError:
                continue  # this '{' wasn't a JSON object start; keep scanning

    # Strategy 3: try raw text as-is
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


async def main():
    start_time = time.time()

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

    # Run the agent and collect all text output
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    text_chunk = part.text
                    response_text += text_chunk
                    print(text_chunk, end="", flush=True)

    print("\n" + "-" * 50)
    print("\n" + "-" * 50)
    print("Verification:")

    elapsed = round(time.time() - start_time, 2)
    data = extract_json(response_text)

    if data is None:
        print("FAILED: Could not extract valid JSON from the response.")
        print("\n--- Raw response (first 2000 chars) ---")
        print(response_text[:2000])
        log_result(
            script_name="manual_verify_travel",
            query=query,
            results={
                "passed": False,
                "reason": "Could not extract valid JSON from response",
                "valid_json": False,
            },
            extra={"elapsed_seconds": elapsed, "raw_response": response_text},
        )
    else:
        required_keys = ["trip_summary", "itinerary", "budget_breakdown", "landmarks"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            print(f"FAILED: Missing keys in JSON: {missing}")
            log_result(
                script_name="manual_verify_travel",
                query=query,
                results={
                    "passed": False,
                    "reason": f"Missing keys: {missing}",
                    "valid_json": True,
                },
                extra={"elapsed_seconds": elapsed, "raw_response": response_text},
            )
        else:
            print("PASSED: Output contains all required JSON keys.")
            landmarks_count = len(data.get('landmarks', []))
            itinerary_days = len(data.get('itinerary', []))
            print(f"Landmarks count: {landmarks_count}")
            print(f"Itinerary days:  {itinerary_days}")
            print("\n--- Extracted JSON ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            log_result(
                script_name="manual_verify_travel",
                query=query,
                results={
                    "passed": True,
                    "valid_json": True,
                    "landmarks_count": landmarks_count,
                    "itinerary_days": itinerary_days,
                },
                extra={"elapsed_seconds": elapsed, "raw_response": response_text},
            )


if __name__ == "__main__":
    asyncio.run(main())
