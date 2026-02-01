from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from AI_Agents.schemas import criterion
import os
from dotenv import load_dotenv


load_dotenv()


judge_prompt = """
You are an expert travel plan evaluator.

Your task is to check if a generated travel plan meets the requirements specified in the user's query.

You will be given:
1. A User Query (containing requirements like Origin, Destination, Budget, Duration, etc.)
2. A Travel Plan (a structured JSON object containing 'itinerary', 'landmarks', 'trip_summary', etc.)

You must extract the following constraints from the Query:
- Origin City
- Destination City(s)
- Duration (Days)
- Budget
- Number of People
- Dates

Then, check if the Plan satisfies ALL these constraints.

Parsing the plan:
- Look at 'trip_summary' for high-level details.
- Check 'budget_breakdown' and individual activity costs for budget compliance.
- Check 'trip_dates' and 'itinerary' length for duration compliance.

Output Format:
Return ONLY a JSON object with:
- "passed": boolean
- "reason": string
- "failed_constraints": list of strings

Do not explain. Do not output markdown.
"""

judge_agent = Agent(
    model=LiteLlm(
        model="openrouter/z-ai/glm-4.5-air:free",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1"
    ),
    name="judge_agent",
    description="Evaluates whether a generated travel plan satisfies user constraints.",
    instruction=judge_prompt,
    output_schema=criterion
)
