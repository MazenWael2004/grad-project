from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel, Field  
class schema(BaseModel):
    passed: bool = Field(description="Whether the travel plan satisfies all constraints.")
    reason: str = Field(description="A brief explanation of why it passed or failed.")
    failed_constraints: list[str] = Field(description="List of specific constraints that were not met.")

judge_agent = Agent(
    model='gemini-2.5-flash',
    name='judge_agent',
    description='An agent that evaluates travel plans against user queries.',
    instruction='''
    You are an expert travel plan evaluator.
    Your task is to check if a generated travel plan meets the requirements specified in the user's query.
    
    You will be given:
    1. A User Query (containing requirements like Origin, Destination, Budget, Duration, etc.)
    2. A Travel Plan (text or structured output)
    
    You must extract the following constraints from the Query:
    - Origin City
    - Destination City(s)
    - Duration (Days)
    - Budget
    - Number of People
    - Dates
    
    Then, check if the Plan satisfies ALL these constraints.
    
    Output Format:
    Return a JSON object with the following fields:
    - "pass": boolean (true if all constraints are met, false otherwise)
    - "reason": string (a brief explanation of why it passed or failed)
    - "failed_constraints": list of strings (list the specific constraints that were not met, e.g. ["Budget", "Duration"], or empty list if passed)
    
    Do not output markdown code blocks, just the JSON string.
    ''',
    output_schema=schema
)
