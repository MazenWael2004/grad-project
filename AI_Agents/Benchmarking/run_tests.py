"""
run_tests.py -- Benchmarking test runner.

This script runs each prompt variant in the rubrics/prompts folder,
measures execution metrics, grades them against the specified rubrics in
rubrics/cairo_trip_rubrics.md and judge.py, and saves the results in rubrics/results.
"""

import sys
import os
import asyncio
import json
import re
import time
import warnings
import yaml

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv


env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Travel_planner', '.env'))
load_dotenv(env_path)
load_dotenv()

from AI_Agents.Travel_planner.agent import root_agent
from AI_Agents.Travel_planner.planner_agent import planner_agent
from AI_Agents.Travel_planner.schema_formatter_agent import schema_formatter_agent
from AI_Agents.Travel_planner.research_agent import research_agent
from AI_Agents.Benchmarking.judge import judge_agent

# Override models to gemini-2.5-flash to avoid model availability and stability issues
MODEL_NAME = "gemini-2.5-flash"
planner_agent.model = MODEL_NAME
schema_formatter_agent.model = MODEL_NAME
research_agent.model = MODEL_NAME
judge_agent.model = MODEL_NAME

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from AI_Agents.Benchmarking.judge import judge_agent
import AI_Agents.Travel_planner.tools as travel_tools
from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel, Field

# Global tool call counter
main_tool_calls = 0

original_search_tool = travel_tools.search_tool
original_calculate_distance_tool = travel_tools.calculate_distance_tool

def wrapped_search_tool(*args, **kwargs):
    global main_tool_calls
    main_tool_calls += 1
    return original_search_tool(*args, **kwargs)

def wrapped_calculate_distance_tool(*args, **kwargs):
    global main_tool_calls
    main_tool_calls += 1
    return original_calculate_distance_tool(*args, **kwargs)

# Instrument the tools
travel_tools.search_tool = wrapped_search_tool
travel_tools.calculate_distance_tool = wrapped_calculate_distance_tool

# Grader LLM Rubric Agent Definition
class AssertionResult(BaseModel):
    assertion: str = Field(description="The assertion being checked")
    passed: bool = Field(description="True if the assertion is satisfied, False otherwise")
    reason: str = Field(description="Brief explanation of why the assertion passed or failed")

class GraderOutput(BaseModel):
    results: list[AssertionResult] = Field(description="List of results for each assertion")

grader_prompt = """
You are an independent quality assurance evaluator for a travel planning AI.
Your task is to grade a generated Travel Plan against a list of assertions and the original User Query.

For each assertion provided in the request, evaluate whether the Travel Plan satisfies it.
Return a structured JSON object with the pass/fail status and a brief reason for each assertion.
"""

grader_agent = Agent(
    model="gemini-3-flash-preview",
    name="grader_agent",
    description="Grades generated travel plans against a list of assertions.",
    instruction=grader_prompt,
    output_schema=GraderOutput
)


def extract_json_from_response(response_text):
    """Extract a JSON object from response text."""
    clean_text = response_text.strip()
    code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(code_block_pattern, clean_text, re.DOTALL)
    if match:
        clean_text = match.group(1).strip()
    try:
        data = json.loads(clean_text)
        return data, clean_text
    except json.JSONDecodeError:
        return None, None


async def run_travel_planner(query):
    """Run the travel planner agent and measure metrics."""
    global main_tool_calls
    main_tool_calls = 0  # Reset counter
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="travel_planner_app",
        session_service=session_service
    )

    user_id = "bench_user"
    session_id = f"session_{int(time.time())}"
    await session_service.create_session(
        app_name="travel_planner_app",
        user_id=user_id,
        session_id=session_id
    )

    response_text = ""
    agent_turns = 0
    start_time = time.time()
    first_token_time = None

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    if first_token_time is None:
                        first_token_time = time.time()
                    response_text += part.text
            agent_turns += 1

    end_time = time.time()

    time_to_first = (first_token_time - start_time) if first_token_time else 0.0
    time_to_last = end_time - start_time
    
    # Count tokens using the model's tokenizer
    try:
        from google import genai
        client = genai.Client()
        input_token_count = client.models.count_tokens(
            model=MODEL_NAME, contents=query
        )
        output_token_count = client.models.count_tokens(
            model=MODEL_NAME, contents=response_text
        )
        input_tokens = input_token_count.total_tokens
        output_tokens = output_token_count.total_tokens
    except Exception:
        # Fallback to estimation if token counting fails
        input_tokens = int(len(query.split()) * 1.33)
        output_tokens = int(len(response_text.split()) * 1.33)
    total_tokens = input_tokens + output_tokens
    
    tokens_per_sec = output_tokens / time_to_last if time_to_last > 0 else 0.0

    metrics = {
        "n_turns": agent_turns,
        "n_toolcalls": main_tool_calls,
        "n_total_tokens": total_tokens,
        "latency": {
            "time_to_first_token": round(time_to_first, 3),
            "output_tokens_per_sec": round(tokens_per_sec, 2),
            "time_to_last_token": round(time_to_last, 3)
        }
    }

    return response_text, metrics


async def grade_assertions(query, plan_json_str, assertions):
    """Run grader agent to evaluate rubric assertions."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=grader_agent,
        app_name="grader_app",
        session_service=session_service
    )
    user_id = "grader_user"
    session_id = f"session_{int(time.time())}"
    await session_service.create_session(
        app_name="grader_app",
        user_id=user_id,
        session_id=session_id
    )

    prompt = f"""
User Query:
{query}

Travel Plan:
{plan_json_str}

Assertions to check:
{json.dumps(assertions, indent=2)}
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

    grader_data, _ = extract_json_from_response(response_text)
    return grader_data


async def run_judge(query, plan_json_str):
    """Run spatial and constraint judge agent."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=judge_agent,
        app_name="judge_app",
        session_service=session_service
    )
    user_id = "judge_user"
    session_id = f"session_{int(time.time())}"
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

    judge_data, _ = extract_json_from_response(response_text)
    return judge_data


async def main():
    benchmarking_dir = os.path.dirname(os.path.abspath(__file__))
    rubrics_path = os.path.join(benchmarking_dir, "rubrics", "cairo_trip_rubrics.md")
    prompts_dir = os.path.join(benchmarking_dir, "rubrics", "prompts")
    results_dir = os.path.join(benchmarking_dir, "rubrics", "results")
    
    os.makedirs(results_dir, exist_ok=True)

    print(f"Loading rubrics from: {rubrics_path}")
    with open(rubrics_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Extract assertions
    assertions = []
    for grader in config.get("graders", []):
        if grader.get("type") == "llm_rubric" and "cairo_trip_rubrics.md" in grader.get("rubric", ""):
            assertions = grader.get("assertions", [])

    print(f"Loaded {len(assertions)} assertions to evaluate.")

    # Find prompt files
    prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith(".md")]
    print(f"Found {len(prompt_files)} prompt files to test.")

    for prompt_file in prompt_files:
        prompt_path = os.path.join(prompts_dir, prompt_file)
        print("\n" + "=" * 60)
        print(f"RUNNING PROMPT: {prompt_file}")
        print("=" * 60)

        with open(prompt_path, "r", encoding="utf-8") as f:
            query = f.read().strip()

        print(f"Query: {query}")
        
        try:
            # 1. Run Travel Planner
            print("\nGenerating travel plan...")
            plan_text, metrics = await run_travel_planner(query)
            plan_data, plan_json_str = extract_json_from_response(plan_text)
            
            if not plan_data:
                print("Failed to parse generated plan as JSON.")
                plan_json_str = "{}"
            
            # 2. Run Grader 1 (LLM Rubric Assertions)
            print("Grading rubric assertions...")
            llm_rubric_results = await grade_assertions(query, plan_json_str, assertions)
            
            # 3. Run Grader 2 (Spatial/Constraint Judge)
            print("Running judge agent...")
            judge_results = await run_judge(query, plan_json_str)

            # Compile results
            result_data = {
                "prompt_file": prompt_file,
                "query": query,
                "metrics": metrics,
                "grading_results": {
                    "llm_rubric_grader": llm_rubric_results,
                    "judge_grader": judge_results
                },
                "generated_plan": plan_data
            }

            # Save results
            result_filename = f"{os.path.splitext(prompt_file)[0]}_result.json"
            result_path = os.path.join(results_dir, result_filename)
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2)

            print(f"[SUCCESS] Saved results to {result_path}")
            print(f"  Latency (last token): {metrics['latency']['time_to_last_token']}s")
            print(f"  Tool calls:           {metrics['n_toolcalls']}")
            if judge_results:
                print(f"  Judge Passed:         {judge_results.get('passed')}")
                print(f"  Spatial Score:        {judge_results.get('spatial_score')}")

        except Exception as e:
            print(f"[ERROR] Failed to run test for {prompt_file}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
