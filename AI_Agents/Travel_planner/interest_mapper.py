INTEREST_TO_CATEGORIES = {
    1: ["entertainment", "relaxation"],     # Nile Cruise
    2: ["architecture", "culture"],          # Photographing
    3: ["nature", "relaxation"],             # Eco Tourism
    4: ["history", "culture", "museum"],     # Cultural Tourism
    5: ["entertainment", "adventure"],       # Camel Riding
    6: ["entertainment", "culture"],         # Festivals and Events
    7: ["nature", "adventure"],              # Road Trips
    8: ["food", "culture"],                  # Food Tourism
    9: ["adventure", "nature"],              # Backpacking
    10: ["art", "museum"],                   # Art Galleries
    11: ["history", "culture", "religion"],  # Cultural Exploration
}

def map_interests_to_categories(interest_ids):
    """
    Maps a list of interest IDs (integers or strings) to database categories.
    Returns a list of unique category strings.
    """
    categories = set()
    for idx in interest_ids:
        try:
            int_id = int(idx)
            if int_id in INTEREST_TO_CATEGORIES:
                categories.update(INTEREST_TO_CATEGORIES[int_id])
        except (ValueError, TypeError):
            continue
    return list(categories)
