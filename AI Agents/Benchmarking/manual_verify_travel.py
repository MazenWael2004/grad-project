import sys
import os
import asyncio

# Add the project root to the python path to allow importing sibling packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Travel_planner.agent import root_agent

async def main():
    query = "Plan a 3-day trip to Paris from London for 2 people with a budget of 1500 USD start date 2024-06-01"
    print(f"Query: {query}\n")
    print("-" * 50)
    # TODO: fix the run_live method and figure out how to call the agent in ADK
    response_text = ""
    async for chunk in root_agent.run_live(prompt=query):
        # Handle different chunk types (similar to evaluations.py pattern)
        if isinstance(chunk, str):
            response_text += chunk
            print(chunk, end="", flush=True)
        elif hasattr(chunk, 'content'):
            content = str(chunk.content)
            response_text += content
            print(content, end="", flush=True)
        elif isinstance(chunk, dict) and 'content' in chunk:
            content = str(chunk['content'])
            response_text += content
            print(content, end="", flush=True)
        else:
            print(str(chunk), end="", flush=True)

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
