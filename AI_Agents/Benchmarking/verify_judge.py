import os
import sys
import pandas as pd
import ast 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from AI_Agents.Benchmarking.evaluations import evaluate_plan
from AI_Agents.Benchmarking.judge import judge_agent

async def verify_judge():
    print("Inspecting judge_agent attributes:")
    try:
        print(f"Output Schema: {judge_agent.output_schema}")
    except Exception as e:
        print(f"Error accessing output_schema: {e}")
    try:
        print(f"Model Config: {judge_agent.model_config}")
    except Exception as e:
        print(f"Error accessing model_config: {e}")

    dataset_path = os.path.join(os.path.dirname(__file__), 'travel_planner.csv')
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"Dataset not found at {dataset_path}")
        return

    # test 1: Pass case (using the reference annotated_plan)
    print("--- Test Case 1: Expecting Pass ---")
    
    first_col = df.columns[0]
    raw_data = df.iloc[0][first_col]
    
    if isinstance(raw_data, str):
        try:
            data = ast.literal_eval(raw_data)
        except (ValueError, SyntaxError):
            print(f"Failed to parse data: {raw_data[:100]}...")
            return
    else:
        print(f"Unexpected data type: {type(raw_data)}")
        return

    query = data.get('query')
    plan = data.get('annotated_plan')
    
    if not query or not plan:
        print("Query or Plan missing in data sample.")
        return
    
    print(f"Query: {query}")
    print(f"Plan (snippet): {str(plan)[:100]}...")
    
    result = await evaluate_plan(query, str(plan))
    print(f"Result: {result}")
    
    if result.get('passed') is True:
        print("PASS: Correctly identified valid plan.")
    else:
        print("FAIL: Incorrectly rejected valid plan.")

    # test 2: Fail case (modify the plan to violate constraints)
    print("\n--- Test Case 2: Expecting Fail ---")
    # Make a broken plan
    bad_plan = "This is a plan for a trip to Paris instead of the requested destination."
    
    print(f"Query: {query}")
    print(f"Bad Plan: {bad_plan}")
    
    result = await evaluate_plan(query, bad_plan)
    print(f"Result: {result}")
    
    if result.get('passed') is False:
        print("PASS: Correctly identified invalid plan.")
    else:
        print("FAIL: Incorrectly accepted invalid plan.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(verify_judge())
