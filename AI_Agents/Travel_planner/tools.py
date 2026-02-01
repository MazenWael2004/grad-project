import json
import os

data_dir = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(data_dir, "egypt_places.json"), "r", encoding="utf-8") as f:
    egypt_places = json.load(f)

with open(os.path.join(data_dir, "hotels.json"), "r", encoding="utf-8") as f:
    hotels = json.load(f)

with open(os.path.join(data_dir, "restaurants.json"), "r", encoding="utf-8") as f:
    restaurants = json.load(f)

def search_tool(query: str) -> str:
   
    query_lower = query.lower()
    results = []
    
   
    if 'hotel' in query_lower or 'accommodation' in query_lower or 'stay' in query_lower:
        
        for hotel in hotels:
            if hotel['city'].lower() in query_lower:
                results.append(
                    f"{hotel['name']} in {hotel['city']}, "
                    f"Price: {hotel['price_per_night']} EGP/night, "
                    f"Rating: {hotel['rating']}/5, "
                    f"Category: {hotel['category']}"
                )
    
    elif 'restaurant' in query_lower or 'food' in query_lower or 'dining' in query_lower or 'eat' in query_lower:
       
        for restaurant in restaurants:
            if restaurant['city'].lower() in query_lower:
                results.append(
                    f"{restaurant['name']} in {restaurant['city']}, "
                    f"Cuisine: {restaurant['cuisine']}, "
                    f"Average meal: {restaurant['average_meal_cost']} EGP, "
                    f"Rating: {restaurant['rating']}/5, "
                    f"Specialty: {restaurant['specialty']}"
                )
    
    else:
    
        for place in egypt_places:
            if place['city'].lower() in query_lower or place['name'].lower() in query_lower:
                results.append(
                    f"{place['name']} in {place['city']}, "
                    f"Cost: {place['average_cost']} EGP, "
                    f"Duration: {place['visit_duration_hours']}h, "
                    f"Best time: {place['best_time']}"
                )
    
   
    if results:
        return "\n".join(results[:10])  
    
    try:
        from duckduckgo_search import DDGS
        online_results = DDGS().text(query, max_results=5)
        formatted_output = [
            f"Title: {r.get('title')}\nSnippet: {r.get('body')}" 
            for r in online_results
        ]
        return "\n\n".join(formatted_output)
    except Exception as e:
        return f"No local results found for '{query}'. Online search unavailable: {str(e)}"
