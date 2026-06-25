from google.adk.agents.sequential_agent import SequentialAgent
from .planner_agent import planner_agent

# Simplified travel planner agent pipeline containing only the planner_agent.
# The research phase is now handled deterministically by database queries and spatial clustering.
root_agent = SequentialAgent(
    name="root_agent",
    description="Arranges pre-clustered database travel records into a formatted TripPlan.",
    sub_agents=[planner_agent],
)