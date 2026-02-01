import sys
import os
import json
import asyncio

# Add the project root to the python path to import judge.agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from judge.agent import judge_agent


async def call_judge(prompt: str) -> str:
    """
    Calls the judge agent asynchronously and returns its raw text output.
    """
    response = await judge_agent.run(prompt)
    
    # ADK returns a structured response, extract text safely
    if hasattr(response, "output"):
        return str(response.output)
    return str(response)


def evaluate_plan(query, plan):
    """
    Evaluates a travel plan against a user query using the Judge Agent.

    Args:
        query (str): The user's query containing travel requirements.
        plan (str): The generated travel plan (TripPlan JSON).

    Returns:
        dict: The evaluation result containing 'pass', 'reason', and 'failed_constraints'.
    """

    prompt = f"""
User Query:
{query}

Travel Plan:
{plan}
"""

    try:
        # Run the async judge call
        response_text = asyncio.run(call_judge(prompt))
    except Exception as e:
        return {
            "pass": False,
            "reason": f"System Error calling judge agent: {str(e)}",
            "failed_constraints": ["System Error"]
        }

    try:
        # Clean markdown if exists
        cleaned_response = (
            response_text
            .replace('```json', '')
            .replace('```', '')
            .strip()
        )

        result = json.loads(cleaned_response)
        return result

    except (json.JSONDecodeError, TypeError) as e:
        return {
            "pass": False,
            "reason": f"Failed to parse judge output: {response_text} (Error: {str(e)})",
            "failed_constraints": ["Output Format"]
        }


# result = evaluate_plan(user_query, trip_plan_json)

# print(result)