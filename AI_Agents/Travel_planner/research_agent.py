from google.adk.agents.llm_agent import Agent
from .tools import search_tool
from google.adk.models.lite_llm import LiteLlm
import os

research_prompt = """
You are a travel research specialist.

### STRICT RULES — READ FIRST:
- Use the search tool a MAXIMUM of 3 times total.
- Do NOT repeat similar searches.
- Once you have hotels, restaurants, and attractions data, STOP and return findings immediately.
- Do NOT search more than once per category.

### Your Research Areas:
1. **Hotels & Accommodation**
   - Provide hotels in the destination city with estimated prices, ratings, and locations
   - Include budget, mid-range, and luxury options based on the user's budget
   - Include approximate addresses and coordinates

2. **Restaurants & Dining**
   - Recommend restaurants for breakfast, lunch, and dinner near attractions or hotels
   - Include local cuisine recommendations and price ranges
   - Note ratings and popular dishes

3. **Tourist Attractions**
   - Identify major landmarks, museums, parks, and points of interest
   - Include typical opening hours, ticket prices, and estimated visit duration
   - Provide accurate coordinates for map plotting

### Instructions:
- Focus on the destination city/cities mentioned in the user's query
- Consider the user's budget when recommending places
- Prioritize popular and well-known locations
- Include specific names, locations, and prices where known
- Use your knowledge of real places and the search tool to get accurate details

### Output Format:
Provide a structured summary of your research findings organized by category:
- Hotels (with estimated prices per night)
- Restaurants (with estimated meal prices)
- Attractions (with ticket prices and coordinates)

Be specific and provide well-known, real locations with accurate information.
DO NOT ask for clarification or suggest changing the budget. Just provide the best options you found.



"""

research_agent = Agent( 
   # model=LiteLlm(
   #    model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
   #    api_key=os.getenv("OPENROUTER_API_KEY"),
   #    api_base="https://openrouter.ai/api/v1"
   # ),
   model=LiteLlm(
    model="gemini/gemini-2.0-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
  ),
   # model = "gemini-3.5-flash",
   #  model=LiteLlm(
   #    model="openai/custom-model",
   #    api_base="https://sd-omar04--vllm-inference-serve.modal.run",
   #    api_key="still_havent_secured_it"
   #  ), 
    name="research_agent",
    description="Provides travel information including hotels, restaurants, and tourist attractions with prices and locations.",
    instruction=research_prompt,
    tools=[search_tool]
)
