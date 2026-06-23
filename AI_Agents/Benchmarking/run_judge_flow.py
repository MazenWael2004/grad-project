"""
run_judge_flow.py -- End-to-end benchmarking: generate a travel plan then judge it.

This script runs the full travel planner pipeline to generate a plan,
then feeds both the original query and the generated plan into the
judge agent (with spatial coherence checking) and the deterministic
spatial verifier for a complete evaluation.

Usage:
    python run_judge_flow.py
"""

import sys
import os
import asyncio
import json
import re
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv

# Load env from AI_Agents root and project root
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
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

# Import judge agent runner and spatial verifier
from AI_Agents.Benchmarking.judge import judge_agent
from AI_Agents.Benchmarking.verify_spatial import analyze_spatial_coherence, print_spatial_report
from AI_Agents.Benchmarking.benchmark_logger import log_result
from pydantic import ValidationError
from AI_Agents.schemas import TripPlan


def extract_json_from_response(response_text):
    """
    Extract a JSON object from the raw LLM response text.
    Handles markdown code blocks and plain JSON.

    Returns:
        (dict, str) -- parsed dict and the clean JSON string, or (None, None) on failure.
    """
    clean_text = response_text.strip()

    # Try to extract from ```json ... ``` code block
    code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(code_block_pattern, clean_text, re.DOTALL)
    if match:
        clean_text = match.group(1).strip()

    try:
        data = json.loads(clean_text)
        return data, clean_text
    except json.JSONDecodeError:
        return None, None


async def generate_plan(query):
    """
    Run the travel planner agent and return the raw response text.
    """
    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name="travel_planner_app",
        session_service=session_service
    )

    user_id = "bench_user"
    session_id = "bench_session"

    await session_service.create_session(
        app_name="travel_planner_app",
        user_id=user_id,
        session_id=session_id
    )

    response_text = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                    print(part.text, end="", flush=True)

    print()
    return response_text


async def run_judge(query, plan_json_str):
    """
    Run the judge agent on the query + plan using an ADK Runner.
    Returns the raw response text from the judge.
    """
    session_service = InMemorySessionService()

    runner = Runner(
        agent=judge_agent,
        app_name="judge_app",
        session_service=session_service
    )

    user_id = "judge_user"
    session_id = "judge_session"

    await session_service.create_session(
        app_name="judge_app",
        user_id=user_id,
        session_id=session_id
    )

    prompt = f"""User Query:
{query}

Travel Plan:
{plan_json_str}
"""

    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    return response_text


async def main():
    start_time = time.time()
    query = (
        "Plan a 3-day trip to cairo from saudi arabia riyadh for 2 people "
        "with a budget of 1500 SAR start date 2026-06-01 and recommanded "
        "resturants and hotels"
    )

    # ── Step 1: Generate the travel plan ─────────────────────────────────
    print("=" * 70)
    print("  STEP 1: GENERATING TRAVEL PLAN")
    print("=" * 70)
    print(f"\nQuery: {query}\n")
    print("-" * 50)

    response_text = await generate_plan(query)

    print("-" * 50)

    # ── Step 2: Parse the plan ───────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  STEP 2: PARSING PLAN OUTPUT")
    print("=" * 70)

    plan_data, plan_json_str = extract_json_from_response(response_text)

    if plan_data is None:
        print("\n[FAIL] Could not parse travel plan as JSON.")
        print("Raw output (first 500 chars):")
        print(response_text[:500])
        return

    # Validate against Pydantic schema
    schema_valid = False
    validation_errors = []
    try:
        TripPlan.model_validate(plan_data)
        schema_valid = True
        print(f"\n[OK] Plan JSON passes full Pydantic schema validation.")
        print(f"  Trip name:      {plan_data.get('trip_name', 'N/A')}")
        print(f"  Dates:          {plan_data.get('trip_dates', 'N/A')}")
        print(f"  Landmarks:      {len(plan_data.get('landmarks', []))}")
        print(f"  Itinerary days: {len(plan_data.get('itinerary', []))}")
    except ValidationError as e:
        print(f"\n[FAIL] Pydantic schema validation failed:")
        for err in e.errors():
            loc = ' -> '.join(str(l) for l in err['loc'])
            print(f"  - {loc}: {err['msg']}")
        validation_errors = [f"{' -> '.join(str(l) for l in err['loc'])}: {err['msg']}" for err in e.errors()]

    # ── Step 3: Deterministic spatial check ──────────────────────────────
    print("\n" + "=" * 70)
    print("  STEP 3: SPATIAL COHERENCE CHECK (deterministic)")
    print("=" * 70)

    spatial_result = analyze_spatial_coherence(plan_data)
    print_spatial_report(spatial_result, plan_data.get("trip_name", "Generated Plan"))

    # ── Step 4: Run the judge agent ──────────────────────────────────────
    print("=" * 70)
    print("  STEP 4: JUDGE AGENT EVALUATION")
    print("=" * 70)

    print("\nRunning judge agent (constraint + spatial)...\n")

    judge_data = None
    judge_response = None
    try:
        judge_response = await run_judge(query, plan_json_str)

        judge_data, _ = extract_json_from_response(judge_response)

        if judge_data:
            print("Judge verdict:")
            print(f"  Passed:             {judge_data.get('passed', 'N/A')}")
            print(f"  Reason:             {judge_data.get('reason', 'N/A')}")
            print(f"  Failed constraints: {judge_data.get('failed_constraints', [])}")
            print(f"  Spatial issues:     {judge_data.get('spatial_issues', [])}")
            print(f"  Spatial score:      {judge_data.get('spatial_score', 'N/A')}")
        else:
            print("[WARN] Could not parse judge output as JSON.")
            print(f"Raw judge response:\n{judge_response}")

    except Exception as e:
        print(f"[ERROR] Judge agent failed: {e}")

    # -- Summary --
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Spatial score (deterministic): {spatial_result['spatial_score']:.0%}")
    print(f"  Spatial issues found:          {spatial_result['flagged_transitions']}")
    if judge_data:
        print(f"  Judge passed:                  {judge_data.get('passed', 'N/A')}")
    else:
        print(f"  Judge passed:                  N/A (judge failed)")
    print("=" * 70)

    # -- Log results --
    log_result(
        script_name="run_judge_flow",
        query=query,
        results={
            "plan_valid_json": plan_data is not None,
            "plan_missing_keys": validation_errors if plan_data else None,
            "schema_valid": schema_valid if plan_data else False,
            "trip_name": plan_data.get("trip_name") if plan_data else None,
            "landmarks_count": len(plan_data.get("landmarks", [])) if plan_data else 0,
            "itinerary_days": len(plan_data.get("itinerary", [])) if plan_data else 0,
            "spatial_score": spatial_result["spatial_score"],
            "spatial_coverage": spatial_result.get("coverage", 0),
            "spatial_flagged_transitions": spatial_result["flagged_transitions"],
            "spatial_total_transitions": spatial_result["total_transitions"],
            "spatial_issues": spatial_result["spatial_issues"],
            "judge_passed": judge_data.get("passed") if judge_data else None,
            "judge_reason": judge_data.get("reason") if judge_data else None,
            "judge_failed_constraints": judge_data.get("failed_constraints", []) if judge_data else [],
        },
        extra={
            "elapsed_seconds": elapsed,
            "raw_plan_response": response_text,
            "raw_judge_response": judge_response,
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
