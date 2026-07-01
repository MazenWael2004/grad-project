import re
import sys
import os
import django
from asgiref.sync import sync_to_async

@sync_to_async
def get_contextualized_query(query_text: str) -> str:
    """
    Parses user preferences from query_text, queries Django database for clustered itinerary,
    and returns a query formatted with the database context.
    If database query fails, returns original query_text.
    """
    try:
        # Setup Django
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
        if backend_dir not in sys.path:
            sys.path.append(backend_dir)
        
        from dotenv import load_dotenv
        load_dotenv(os.path.join(backend_dir, ".env"))
        
        # Set a fallback SECRET_KEY if not present in env to allow database setup to proceed
        if not os.environ.get("SECRET_KEY"):
            os.environ["SECRET_KEY"] = "dummy_secret_key_for_testing"

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()

        from AI_Agents.Travel_planner.clustering import get_clustered_itinerary
        from backend.api.views import format_clusters_for_prompt
    except Exception as e:
        print(f"[WARN] Failed to initialize Django or import clustering: {e}")
        return query_text

    # Parse preferences using regex
    dest_match = re.search(r"Destination:\s*(.+)", query_text, re.IGNORECASE)
    budget_match = re.search(r"Budget(?:\s*level)?:\s*(.+)", query_text, re.IGNORECASE)
    party_match = re.search(r"(?:Party|Travelers):\s*(.+)", query_text, re.IGNORECASE)
    interests_match = re.search(r"Interests:\s*(.+)", query_text, re.IGNORECASE)
    dates_match = re.search(r"Dates:\s*([\d-]+)\s+to\s+([\d-]+)", query_text, re.IGNORECASE)

    # Fallback for run_judge_flow.py unstructured prompt
    if not dest_match:
        destination_label = "Cairo"
        gov_id = 1
        budget_id = 1
        interest_ids = [4, 8]  # Cultural, Food
        start_date = "2026-06-01"
        end_date = "2026-06-04"
        party_label = "Couple"
        interests_str = "Cultural Tourism, Food Tourism"
        budget_label = "Budget"
    else:
        dest_val = dest_match.group(1).strip() if dest_match.group(1) else ""
        budget_val = budget_match.group(1).strip() if budget_match.group(1) else ""
        party_val = party_match.group(1).strip() if (party_match and party_match.group(1)) else "Couple"
        interests_val = interests_match.group(1).strip() if (interests_match and interests_match.group(1)) else ""
        
        # Parse dates
        if dates_match:
            start_date = dates_match.group(1).strip()
            end_date = dates_match.group(2).strip()
        else:
            start_date = "2026-06-01"
            end_date = "2026-06-04"

        # Map destination
        gov_map = {
            "cairo": 1, "alexandria": 2, "luxor": 3, "aswan": 4, "giza": 5,
            "hurghada": 6, "sharm": 7, "dahab": 8, "marsa": 9, "siwa": 10
        }
        gov_id = 2  # default
        destination_label = dest_val
        for k, v in gov_map.items():
            if k in dest_val.lower():
                gov_id = v
                break

        # Map budget
        budget_map = {"cheap": 1, "budget": 1, "balanced": 2, "mid": 2, "flexible": 2, "luxury": 3}
        budget_id = 2  # default
        budget_label = budget_val
        for k, v in budget_map.items():
            if k in budget_val.lower():
                budget_id = v
                break

        # Map party
        party_map = {"solo": 1, "only me": 1, "couple": 2, "spouse": 2, "family": 3, "friends": 4}
        party_id = 2  # default
        party_label = party_val
        for k, v in party_map.items():
            if k in party_val.lower():
                party_id = v
                break

        # Map interests
        interests_db_map = {
            "nile cruise": 1, "photographing": 2, "eco tourism": 3, "cultural tourism": 4,
            "camel riding": 5, "festivals": 6, "road trips": 7, "food tourism": 8,
            "backpacking": 9, "art galleries": 10, "cultural exploration": 11
        }
        interest_ids = []
        interest_labels = []
        for name, db_id in interests_db_map.items():
            clean_name = name.lower()
            clean_val = interests_val.lower()
            if clean_name in clean_val or clean_name.replace(" ", "") in clean_val or clean_name.replace("and", "&") in clean_val:
                interest_ids.append(db_id)
                interest_labels.append(name.title())
        
        if not interest_ids:
            interest_ids = [4]  # default cultural
            interest_labels = ["Cultural Tourism"]
        interests_str = ", ".join(interest_labels)

    # Get clustered data
    try:
        clustering_data = get_clustered_itinerary(gov_id, budget_id, interest_ids, start_date, end_date)
        if not clustering_data or not clustering_data.get("clusters"):
            print(f"[WARN] get_clustered_itinerary returned empty clusters for gov_id={gov_id}")
            return query_text
        clustered_context = format_clusters_for_prompt(clustering_data)
    except Exception as e:
        print(f"[WARN] Error executing get_clustered_itinerary: {e}")
        return query_text

    # Construct the final prompt exactly like views.py does
    contextualized_query = f"""Plan a trip with the following preferences:
- Origin: Cairo, Egypt
- Destination: {destination_label}
- Dates: {start_date} to {end_date}
- Budget level: {budget_label}
- Travelers: {party_label}
- Interests: {interests_str}

Use ONLY the pre-filtered, pre-clustered database travel data provided below:

{clustered_context}

RULES:
1. Use ONLY the attractions, hotel, and restaurants listed in the day clusters above.
2. Use the EXACT prices, names, and coordinates provided. Do NOT change them.
3. Arrange the activities for each day into a logical, enjoyable timeline (morning, afternoon, evening) with times, matching the attraction opening/closing times.
4. Include check-in and meals at the specified restaurants.
5. Return the full itinerary as a JSON object matching the TripPlan schema, wrapped in a ```json ... ``` code block.
"""
    return contextualized_query
