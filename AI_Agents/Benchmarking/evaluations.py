import sys
import os
import json

# Add the project root to the python path to import judge.agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from judge.agent import judge_agent

import asyncio

def evaluate_plan(query, plan):
    """
    Evaluates a travel plan against a user query using the Judge Agent.
    
    Args:
        query (str): The user's query containing travel requirements.
        plan (str): The generated travel plan.
        
    Returns:
        dict: The evaluation result containing 'pass', 'reason', and 'failed_constraints'.
    """
    
    prompt = f"""
    User Query:
    {query}
    
    Travel Plan:
    {plan}
    """
    
    def get_response(p):
        response_text = ""
        
        return response_text

    # Send the prompt to the judge agent
    try:
        response = get_response(prompt)
    except Exception as e:
        return {
            "pass": False,
            "reason": f"System Error calling judge agent: {str(e)}",
            "failed_constraints": ["System Error"]
        }

    try:
        # Simple cleanup to ensure we get JSON (sometimes models add markdown blocks)
        # Check if response is string, otherwise cast or handle
        if not isinstance(response, str):
             response_str = str(response)
        else:
             response_str = response
             
        cleaned_response = response_str.replace('```json', '').replace('```', '').strip()
        result = json.loads(cleaned_response)
        return result
    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        return {
            "pass": False,
            "reason": f"Failed to parse judge output: {response} (Error: {str(e)})",
            "failed_constraints": ["Output Format"]
        }
