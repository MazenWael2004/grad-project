import math
from datetime import datetime, date
from django.db.models import Q
from apps.attractions.models import Governorate, Attraction, Hotel, Restaurant
from .interest_mapper import map_interests_to_categories

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_clustered_itinerary(gov_id, budget_id, interest_ids, start_date_str, end_date_str):
    """
    Deterministically filters and clusters attractions, hotels, and restaurants.
    Returns a dictionary of day-by-day clusters with closest matching hotels and restaurants.
    """
    # Parse dates
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        num_days = (end_date - start_date).days + 1
    except Exception:
        num_days = 3  # default fallback
        start_date = date.today()
        end_date = date.today()

    if num_days <= 0:
        num_days = 1

    # 1. Fetch Governorate
    try:
        governorate = Governorate.objects.get(id=gov_id)
    except Governorate.DoesNotExist:
        governorate = Governorate.objects.first()
        if not governorate:
            return {
                "clusters": [],
                "hotel": None,
                "total_estimated_cost": 0,
                "warnings": ["No governorate data found in DB."]
            }

    # 2. Map interests to categories
    categories = map_interests_to_categories(interest_ids)

    # 3. Fetch attractions for this governorate
    attractions_qs = Attraction.objects.filter(governorate=governorate)
    if categories:
        q_obj = Q()
        for cat in categories:
            q_obj |= Q(categories__contains=cat)
        
        filtered_attractions = list(attractions_qs.filter(q_obj))
        # Fallback if too few categories matched
        if len(filtered_attractions) < num_days:
            filtered_attractions = list(attractions_qs)
    else:
        filtered_attractions = list(attractions_qs)

    # Sort attractions by popularity desc, then name
    filtered_attractions.sort(key=lambda x: (-x.popularity, x.name))

    # 4. Fetch hotels for this governorate matching budget
    budget_map = {1: "budget", 2: "mid-range", 3: "luxury"}
    budget_cat = budget_map.get(int(budget_id) if budget_id else 2, "mid-range")
    
    hotels_qs = Hotel.objects.filter(governorate=governorate, category=budget_cat)
    if not hotels_qs.exists():
        hotels_qs = Hotel.objects.filter(governorate=governorate)
    if not hotels_qs.exists():
        hotels_qs = Hotel.objects.all()
    
    hotels = list(hotels_qs)

    # 5. Fetch restaurants for this governorate
    restaurants_qs = Restaurant.objects.filter(governorate=governorate)
    if not restaurants_qs.exists():
        restaurants_qs = Restaurant.objects.all()
    restaurants = list(restaurants_qs)

    # 6. Cluster attractions into num_days using a greedy approach
    unvisited = list(filtered_attractions)
    
    if not unvisited:
        return {
            "clusters": [],
            "hotel": None,
            "total_estimated_cost": 0,
            "warnings": [f"No attractions found in {governorate.name}."]
        }

    days_attractions = [[] for _ in range(num_days)]
    
    # Seed each day with a highly popular attraction
    for d in range(num_days):
        if unvisited:
            days_attractions[d].append(unvisited.pop(0))

    # Distribute the remaining attractions based on distance and daily limit (8 hours)
    while unvisited:
        attraction = unvisited.pop(0)
        best_day = -1
        min_dist = float('inf')
        
        for d in range(num_days):
            day_list = days_attractions[d]
            total_duration = sum(a.visit_duration_hours for a in day_list)
            if total_duration + attraction.visit_duration_hours > 8.0:
                continue
                
            if not day_list:
                dist = 0
            else:
                dist = sum(calculate_distance(attraction.latitude, attraction.longitude, a.latitude, a.longitude) for a in day_list) / len(day_list)
            
            if dist < min_dist:
                min_dist = dist
                best_day = d
                
        if best_day == -1:
            # Fallback to the day with the minimum hours spent
            best_day = min(range(num_days), key=lambda d: sum(a.visit_duration_hours for a in days_attractions[d]))
            
        days_attractions[best_day].append(attraction)

    # 7. Select one hotel closest to all selected attractions centroid
    all_selected_attractions = []
    for day_list in days_attractions:
        all_selected_attractions.extend(day_list)
        
    selected_hotel = None
    if hotels and all_selected_attractions:
        avg_lat = sum(a.latitude for a in all_selected_attractions) / len(all_selected_attractions)
        avg_lon = sum(a.longitude for a in all_selected_attractions) / len(all_selected_attractions)
        selected_hotel = min(hotels, key=lambda h: calculate_distance(h.latitude, h.longitude, avg_lat, avg_lon))
    elif hotels:
        selected_hotel = hotels[0]

    # 8. Build structured day clusters
    structured_clusters = []
    total_attractions_cost = 0
    warnings = []

    for d in range(num_days):
        day_attractions = days_attractions[d]
        time_order = {"morning": 1, "afternoon": 2, "evening": 3}
        day_attractions.sort(key=lambda x: time_order.get(x.best_time, 2))
        
        # Select 2 restaurants closest to the day's first attraction
        day_restaurants = []
        if day_attractions and restaurants:
            ref_a = day_attractions[0]
            sorted_restaurants = sorted(restaurants, key=lambda r: calculate_distance(r.latitude, r.longitude, ref_a.latitude, ref_a.longitude))
            day_restaurants = sorted_restaurants[:2]
        elif restaurants:
            day_restaurants = restaurants[:2]

        formatted_attractions = []
        for a in day_attractions:
            total_attractions_cost += a.average_cost
            formatted_attractions.append({
                "id": a.id,
                "name": a.name,
                "city": a.city,
                "categories": a.categories,
                "average_cost": a.average_cost,
                "visit_duration_hours": a.visit_duration_hours,
                "opening_time": a.opening_time.strftime("%H:%M") if a.opening_time else "09:00",
                "closing_time": a.closing_time.strftime("%H:%M") if a.closing_time else "18:00",
                "best_time": a.best_time,
                "popularity": a.popularity,
                "latitude": a.latitude,
                "longitude": a.longitude,
                "description": a.description
            })

        formatted_restaurants = []
        for r in day_restaurants:
            formatted_restaurants.append({
                "id": r.id,
                "name": r.name,
                "city": r.city,
                "cuisine": r.cuisine,
                "average_meal_cost": r.average_meal_cost,
                "rating": r.rating,
                "specialty": r.specialty,
                "latitude": r.latitude,
                "longitude": r.longitude
            })

        structured_clusters.append({
            "day": d + 1,
            "day_label": f"Day {d + 1}",
            "attractions": formatted_attractions,
            "restaurants": formatted_restaurants
        })

    hotel_cost = 0
    formatted_hotel = None
    if selected_hotel:
        hotel_cost = selected_hotel.price_per_night * num_days
        formatted_hotel = {
            "id": selected_hotel.id,
            "name": selected_hotel.name,
            "city": selected_hotel.city,
            "price_per_night": selected_hotel.price_per_night,
            "rating": selected_hotel.rating,
            "category": selected_hotel.category,
            "latitude": selected_hotel.latitude,
            "longitude": selected_hotel.longitude
        }

    total_restaurant_cost = 0
    for c in structured_clusters:
        for r in c["restaurants"]:
            total_restaurant_cost += r["average_meal_cost"]

    total_estimated_cost = total_attractions_cost + hotel_cost + total_restaurant_cost

    for d in range(num_days):
        if not days_attractions[d]:
            warnings.append(f"Day {d+1} has no attractions allocated due to limited options.")

    return {
        "clusters": structured_clusters,
        "hotel": formatted_hotel,
        "total_estimated_cost": total_estimated_cost,
        "warnings": warnings
    }
