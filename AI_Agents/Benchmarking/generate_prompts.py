import os
import random
import shutil

def main():
    # Set seed for reproducibility
    random.seed(42)

    # 1. Define options
    governorates = [
        "Cairo Governorate", "Alexandria Governorate", "Luxor Governorate",
        "Aswan Governorate", "Giza Governorate", "Hurghada",
        "Sharm El-Sheikh", "Dahab", "Marsa Matruh", "Siwa"
    ]
    
    origins = ["Cairo", "Alexandria", "Riyadh", "Dubai", "London", "New York", "Paris"]
    budgets = ["Cheap", "Balanced", "Luxury"]
    parties = ["Only Me", "Couple", "Family", "Friends"]
    
    interests_pool = [
        "Nile Cruise", "Photographing", "Eco Tourism", "Cultural Tourism",
        "Camel Riding", "Festivals and Events", "Road Trips", "Food Tourism",
        "Backpacking", "Art Galleries", "Cultural Exploration"
    ]

    # 2. Get directories
    benchmarking_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(benchmarking_dir, "rubrics", "prompts")
    results_dir = os.path.join(benchmarking_dir, "rubrics", "results")

    # 3. Clean and recreate prompts directory
    if os.path.exists(prompts_dir):
        shutil.rmtree(prompts_dir)
    os.makedirs(prompts_dir, exist_ok=True)
    print(f"Cleared and recreated prompts directory: {prompts_dir}")

    # 4. Clean results directory
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)
    print(f"Cleared and recreated results directory: {results_dir}")

    # 5. Generate 50 distinct combinations
    generated_sets = set()
    prompts_count = 50

    while len(generated_sets) < prompts_count:
        dest = random.choice(governorates)
        
        # Ensure origin is not the same as destination governorate
        possible_origins = [o for o in origins if o.lower() not in dest.lower()]
        origin = random.choice(possible_origins)
        
        budget = random.choice(budgets)
        party = random.choice(parties)
        
        # Pick a random number of interests (2 to 4)
        num_interests = random.randint(2, 4)
        interests = random.sample(interests_pool, num_interests)
        
        # Choose trip duration (2 to 5 days) based on date ranges
        # e.g., 2026-08-15 to 2026-08-18 (4 days)
        duration_days = random.randint(2, 5)
        start_day = random.randint(1, 20)
        end_day = start_day + duration_days - 1
        
        # Format dates
        month = random.choice(["05", "06", "07", "08", "09", "10", "11", "12"])
        start_date = f"2026-{month}-{start_day:02d}"
        end_date = f"2026-{month}-{end_day:02d}"
        
        # Unique representation to avoid duplicates
        combo_key = (origin, dest, start_date, end_date, budget, party, tuple(sorted(interests)))
        if combo_key in generated_sets:
            continue
            
        generated_sets.add(combo_key)
        idx = len(generated_sets)

        # Generate filename
        filename = f"trip_prompt_{idx:02d}_{dest.lower().replace(' ', '_').replace('-', '_')}.md"
        filepath = os.path.join(prompts_dir, filename)

        # Generate markdown prompt content
        content = f"""Plan a trip with the following preferences:
Origin: {origin}
Destination: {dest}
Dates: {start_date} to {end_date}
Budget: {budget}
Party: {party}
Interests: {', '.join(interests)}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Successfully generated {prompts_count} distinct test prompts in {prompts_dir}!")

if __name__ == "__main__":
    main()
