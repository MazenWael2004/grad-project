from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from ..schemas import TripPlan
import os

schema_formatter_prompt = """
You are an expert Travel Planner. Your goal is to create detailed, practical, and enjoyable travel itineraries that strictly adhere to the user's constraints.

    ### Process:
    1.  **Analyze the Request:** Identify the following constraints from the input:
        *   **Origin City**
        *   **Destination City(s)**
        *   **Duration** (Number of days)
        *   **Budget** (Total or per person)
        *   **Number of People**
        *   **Dates** (Specific travel dates)

    2.  **Plan the Itinerary:** Create a day-by-day plan that fits strictly within the budget and time constraints. Route logically, ensure realistic activity times, and provide accurate estimated costs.

    3.  **Output Format:**
        You must output a structured JSON object strictly adhering to the schema.
        *   **Landmarks:** Identify key landmarks visited in the trip. For each, provide a specific `id` (e.g., 'cairo_tower'), `title`, `description`, `coordinate` (latitude/longitude), and a `color` hex code for map pins.
        *   **Itinerary:** For each day, provide a list of `activities`. Each activity needs a `time` range, `title`, `description`, `cost` (formatted string like 'EGP 300'), `rating` (float), and `reviews_count` (int).
        *   **Budget Breakdown:** Provide a list of strings summarizing costs.
        *   **Trip Summary:** Provide a high-level summary including dates, travelers, and luxury level.

    Important:
    *   If any constraint is missing (e.g., budget), make a reasonable assumption but state it clearly in the trip summary.
    *   Ensure the total cost does not exceed the user's budget.
    *   Be specific about locations and names of places.
    *   **Coordinates must be accurate real-world coordinates.**
"""

schema_formatter_agent = Agent(
    model=LiteLlm(
        model="openrouter/minimax/minimax-m2.5:free",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1"
    ),
    name="schema_formatter_agent",
    description="Formats travel plans to strictly match the TripPlan Pydantic schema with accurate coordinates and proper structure.",
    instruction=schema_formatter_prompt,
    output_schema=TripPlan
)
