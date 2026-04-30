from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from AI_Agents.schemas import criterion
from AI_Agents.Travel_planner.tools import calculate_distance_tool
import os
from dotenv import load_dotenv


load_dotenv()

# Wrap the distance calculator as an ADK FunctionTool
distance_tool = FunctionTool(calculate_distance_tool)

judge_prompt = """
You are an expert travel plan evaluator with expertise in spatial/geographic reasoning.

Your task is to check if a generated travel plan meets the requirements specified in the user's query,
AND whether the itinerary makes spatial sense (i.e., locations are reachable in the time allocated).

You will be given:
1. A User Query (containing requirements like Origin, Destination, Budget, Duration, etc.)
2. A Travel Plan (a structured JSON object containing 'itinerary', 'landmarks', 'trip_summary', etc.)

## Step 1: Constraint Evaluation
Extract the following constraints from the Query and verify them against the Plan:
- Origin City
- Destination City(s)
- Duration (Days)
- Budget
- Number of People
- Dates

Parsing the plan:
- Look at 'trip_summary' for high-level details.
- Check 'budget_breakdown' and individual activity costs for budget compliance.
- Check 'trip_dates' and 'itinerary' length for duration compliance.

## Step 2: Spatial Coherence Evaluation
For each day in the itinerary:
1. Identify the locations/landmarks mentioned in the activities.
2. Use the 'landmarks' list in the plan to find coordinates (latitude, longitude) for each location.
3. Use the `calculate_distance_tool` to compute the distance (in km) between consecutive activities.
4. Estimate travel time assuming:
   - Urban travel: ~30 km/h average speed
   - Intercity travel: ~80 km/h average speed
5. Flag any issues where:
   - Consecutive activities within the same day are more than 50 km apart without enough time gap
   - Activities in different cities appear on the same day without realistic travel time
   - The travel time between consecutive activities exceeds 2 hours for within-city travel

## Output Format
Return ONLY a JSON object with:
- "passed": boolean (true if all constraints AND spatial checks pass)
- "reason": string (explanation covering both constraint and spatial evaluation)
- "failed_constraints": list of strings (constraint violations)
- "spatial_issues": list of strings (spatial problems found)
- "spatial_score": float from 0.0 to 1.0 (1.0 = perfect spatial coherence)

Do not explain. Do not output markdown.
"""

judge_agent = Agent(
    model=LiteLlm(
        model="openrouter/google/gemini-2.5-flash-preview",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1"
    ),
    name="judge_agent",
    description="Evaluates whether a generated travel plan satisfies user constraints and checks spatial coherence.",
    instruction=judge_prompt,
    tools=[distance_tool],
    output_schema=criterion
)
