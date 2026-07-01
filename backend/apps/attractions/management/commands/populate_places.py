import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.attractions.models import Governorate, Attraction, Hotel, Restaurant

class Command(BaseCommand):
    help = "Populate the database with attractions, hotels, and restaurants from Google Places API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--gov",
            type=str,
            help="Only fetch data for a specific governorate by name (e.g., Siwa, Aswan)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="Limit the number of places fetched per category per governorate (default: 5)",
        )

    def handle(self, *args, **options):
        # 1. Load API Key
        api_key = os.getenv("MAPS_PLATFORM_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.stderr.write(
                "Error: MAPS_PLATFORM_KEY or GOOGLE_API_KEY not found in environment/env files."
            )
            return

        limit = options["limit"]
        gov_filter = options["gov"]

        # Get governorates to process
        if gov_filter:
            governorates = Governorate.objects.filter(name__icontains=gov_filter)
            if not governorates.exists():
                self.stdout.write(self.style.WARNING(f"Governorate '{gov_filter}' not found. Creating it..."))
                # Try to get coordinates using Geocoding if needed, or default
                lat, lon = self.geocode_governorate(gov_filter, api_key)
                gov = Governorate.objects.create(name=gov_filter.title(), latitude=lat, longitude=lon)
                governorates = [gov]
        else:
            governorates = Governorate.objects.all()

        if not governorates:
            self.stdout.write("No governorates found in the database. Please seed governorates first.")
            return

        for gov in governorates:
            self.stdout.write(f"\nProcessing Governorate: {gov.name} ({gov.latitude}, {gov.longitude})")
            
            # Fetch Attractions
            self.fetch_and_save_places(
                gov=gov,
                query=f"tourist attractions in {gov.name}, Egypt",
                category_type="attraction",
                limit=limit,
                api_key=api_key,
            )

            # Fetch Hotels
            self.fetch_and_save_places(
                gov=gov,
                query=f"hotels and resorts in {gov.name}, Egypt",
                category_type="hotel",
                limit=limit,
                api_key=api_key,
            )

            # Fetch Restaurants
            self.fetch_and_save_places(
                gov=gov,
                query=f"restaurants and dining in {gov.name}, Egypt",
                category_type="restaurant",
                limit=limit,
                api_key=api_key,
            )

    def geocode_governorate(self, name, api_key):
        """Geocodes a governorate name to get its coordinates."""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": f"{name}, Egypt", "key": api_key}
        try:
            res = requests.get(url, params=params).json()
            if res.get("status") == "OK" and res.get("results"):
                loc = res["results"][0]["geometry"]["location"]
                return loc["lat"], loc["lng"]
        except Exception as e:
            self.stderr.write(f"Geocoding failed: {e}")
        return 30.0444, 31.2357  # Cairo default

    def fetch_and_save_places(self, gov, query, category_type, limit, api_key):
        self.stdout.write(f"  Fetching {category_type}s...")
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "location": f"{gov.latitude},{gov.longitude}",
            "radius": 15000,  # 15km
            "key": api_key,
        }
        
        try:
            response = requests.get(url, params=params).json()
            if response.get("status") not in ["OK", "ZERO_RESULTS"]:
                err_msg = response.get("error_message", "No details provided.")
                self.stderr.write(f"    Google API returned status: {response.get('status')}. Details: {err_msg}")
                return

            results = response.get("results", [])[:limit]
            self.stdout.write(f"    Found {len(results)} matches.")

            for index, place in enumerate(results):
                name = place.get("name")
                lat = place["geometry"]["location"]["lat"]
                lng = place["geometry"]["location"]["lng"]
                address = place.get("formatted_address", "")
                rating = place.get("rating", 4.0)
                place_id = place.get("place_id")
                types = place.get("types", [])

                # Extract city
                city = self.extract_city(address, gov.name)

                # Fetch and download Photo
                image_path = None
                photos = place.get("photos", [])
                if photos:
                    photo_ref = photos[0].get("photo_reference")
                    subfolder = f"{category_type}s"
                    filename = f"{place_id}.jpg"
                    image_path = self.download_photo(photo_ref, api_key, subfolder, filename)

                if category_type == "attraction":
                    # Map categories
                    categories = self.map_types_to_categories(types)
                    # Determine best_time
                    if "museum" in types or "historical_landmark" in types:
                        best_time = "morning"
                    elif "park" in types or "zoo" in types:
                        best_time = "afternoon"
                    else:
                        best_time = "afternoon"

                    Attraction.objects.update_or_create(
                        name=name,
                        governorate=gov,
                        defaults={
                            "city": city,
                            "latitude": lat,
                            "longitude": lng,
                            "categories": categories,
                            "average_cost": self.get_attraction_cost(name),
                            "visit_duration_hours": 2.0,
                            "best_time": best_time,
                            "popularity": int(round(rating)),
                            "description": f"A popular tourist destination in {gov.name} with a rating of {rating} stars.",
                            "image_url": image_path,
                        }
                    )
                elif category_type == "hotel":
                    # Determine hotel price category
                    price_level = place.get("price_level", 2)
                    if price_level <= 1:
                        category = "budget"
                        price = 450
                    elif price_level == 2:
                        category = "mid-range"
                        price = 1200
                    else:
                        category = "luxury"
                        price = 3500

                    Hotel.objects.update_or_create(
                        name=name,
                        governorate=gov,
                        defaults={
                            "city": city,
                            "latitude": lat,
                            "longitude": lng,
                            "price_per_night": price,
                            "rating": rating,
                            "category": category,
                            "image_url": image_path,
                        }
                    )
                elif category_type == "restaurant":
                    # Map cuisine
                    cuisine = "Local / International"
                    if "cafe" in types:
                        cuisine = "Cafe / Patisserie"
                    elif "seafood_restaurant" in types:
                        cuisine = "Seafood"
                    elif "steakhouse" in types:
                        cuisine = "Steakhouse"

                    price_level = place.get("price_level", 2)
                    avg_meal = 120 if price_level <= 1 else (250 if price_level == 2 else 550)

                    Restaurant.objects.update_or_create(
                        name=name,
                        governorate=gov,
                        defaults={
                            "city": city,
                            "latitude": lat,
                            "longitude": lng,
                            "cuisine": cuisine,
                            "average_meal_cost": avg_meal,
                            "rating": rating,
                            "specialty": "Chef's Specials",
                            "image_url": image_path,
                        }
                    )
                self.stdout.write(f"    Saved {category_type}: {name} (City: {city})")
        except Exception as e:
            self.stderr.write(f"    Error processing {category_type}s: {e}")

    def download_photo(self, photo_ref, api_key, subfolder, filename):
        url = "https://maps.googleapis.com/maps/api/place/photo"
        params = {
            "maxwidth": 800,
            "photo_reference": photo_ref,
            "key": api_key
        }
        try:
            response = requests.get(url, params=params, stream=True)
            if response.status_code == 200:
                media_subfolder = os.path.join(settings.MEDIA_ROOT, subfolder)
                os.makedirs(media_subfolder, exist_ok=True)
                filepath = os.path.join(media_subfolder, filename)
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return f"/media/{subfolder}/{filename}"
        except Exception as e:
            self.stderr.write(f"      Photo download failed: {e}")
        return None

    def extract_city(self, address, gov_name):
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            # If last is Egypt, pop it
            if parts[-1].lower() in ["egypt", "egypt."]:
                parts.pop()
            if len(parts) >= 1:
                return parts[-1]
        return gov_name

    def map_types_to_categories(self, types):
        mapping = {
            "museum": "museum",
            "church": "religion",
            "mosque": "religion",
            "hindu_temple": "religion",
            "synagogue": "religion",
            "park": "nature",
            "zoo": "nature",
            "aquarium": "nature",
            "art_gallery": "culture",
            "amusement_park": "entertainment",
            "shopping_mall": "shopping",
            "market": "shopping",
            "natural_feature": "nature",
            "landmark": "history",
            "historical_landmark": "history",
            "tourist_attraction": "culture",
        }
        categories = set()
        for t in types:
            if t in mapping:
                categories.add(mapping[t])
        if not categories:
            categories.add("culture")
        return list(categories)

    def get_attraction_cost(self, name):
        name_lower = name.lower()
        famous_prices = {
            "pyramid": 700,
            "egyptian museum": 550,
            "grand egyptian": 1200,
            "national museum of egyptian civilization": 500,
            "nmec": 500,
            "citadel of saladin": 450,
            "cairo citadel": 450,
            "khan el khalili": 0,
            "khan el-khalili": 0,
            "karnak": 450,
            "valley of the kings": 600,
            "luxor temple": 400,
            "hatshepsut": 360,
            "philae": 450,
            "abu simbel": 600,
            "bibliotheca alexandrina": 300,
            "alexandria library": 300,
            "qaitbay": 300,
            "pompey": 150,
            "catacombs": 150,
            "shali fortress": 100,
            "oracle temple": 100,
            "temple of the oracle": 100,
            "st. cath": 200,
            "saint cath": 200,
            "ras mohammed": 300,
            "giftun": 800,
            "blue hole": 150,
            "cairo tower": 250,
            "al-azhar park": 40,
            "al azhar park": 40,
        }
        for key, price in famous_prices.items():
            if key in name_lower:
                return price
        return 200  # Default cost EGP
