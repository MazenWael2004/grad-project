from pydantic import BaseModel, Field


class criterion(BaseModel):
    passed: bool = Field(description="Whether the travel plan satisfies all constraints.")
    reason: str = Field(description="A brief explanation of why it passed or failed.")
    failed_constraints: list[str] = Field(description="List of specific constraints that were not met.")
    spatial_issues: list[str] = Field(
        default_factory=list,
        description="List of spatial/distance issues found in the itinerary, e.g. unreachable consecutive activities."
    )
    spatial_score: float = Field(
        default=1.0,
        description="Spatial coherence score from 0.0 (completely incoherent) to 1.0 (perfectly coherent)."
    )

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
