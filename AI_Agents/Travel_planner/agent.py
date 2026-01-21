from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel, Field
prompt ="""
    You are an expert Travel Planner. Your goal is to create detailed, practical, and enjoyable travel itineraries that strictly adhere to the user's constraints.

    ### Process:
    1.  **Analyze the Request:** Identify the following constraints from the user's input:
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

class Coordinate(BaseModel):
    latitude: float = Field(description="Latitude of the location")
    longitude: float = Field(description="Longitude of the location")

class Landmark(BaseModel):
    id: str = Field(description="Unique identifier for the landmark, snake_case")
    title: str = Field(description="Name of the landmark")
    description: str = Field(description="Short description")
    coordinate: Coordinate
    color: str = Field(description="Color for the map pin (e.g., #F59E0B)")

class Activity(BaseModel):
    time: str = Field(description="Time range, e.g., '08:00 AM - 3:00 PM'")
    title: str = Field(description="Name of the activity or place")
    description: str = Field(description="Description of the activity")
    cost: str = Field(description="Estimated cost, e.g., 'EGP 300'")
    rating: float = Field(description="Rating out of 5", default=4.5)
    reviews_count: int = Field(description="Number of reviews", default=100)
    google_maps_url: str = Field(description="Link to view on Google Maps", default="https://maps.google.com")

class DayPlan(BaseModel):
    day: str = Field(description="Day title, e.g., 'Day 1' or 'December 1'")
    activities: list[Activity]

class TripPlan(BaseModel):
    trip_name: str = Field(description="Name of the trip")
    trip_summary: str = Field(description="Brief summary of the trip including origin, destination, etc.")
    trip_dates: str = Field(description="Date range, e.g., 'Dec 12 - Dec 14, 2025'")
    travelers_type: str = Field(description="Type of travelers, e.g., 'Couple', 'Family'")
    luxury_level: str = Field(description="Luxury level, e.g., 'Budget', 'Luxury'")
    itinerary: list[DayPlan]
    budget_breakdown: list[str] = Field(description="A list of estimated costs for flights/transport, accommodation, food, activities, and total.")
    landmarks: list[Landmark] = Field(description="List of landmarks to be plotted on the map")

root_agent = Agent(
    model="gemini-3-flash-preview",
    name= "Travel_planner_agent",
    description="A helpful assistant that generates detailed travel itineraries based on user constraints.",
    instruction=prompt, 
    output_schema=TripPlan,
)
