import os
import re
import json
import random
## random.seed(1)  # comment out for different results each time
import statistics

COMPANY_TYPES = ["Aerospace", "Automotive", "Chemical", "Computer", 
                "Construction", "Education", "Electric", "Energy", 
                "Entertainment", "Film", "Financial", "Fishing",
                "Food", "Healthcare", "Insurance", 
                "Music", "Petroleum", "Pharmaceutical", 
                "Real estate", "Software", "Sports", "Steel", 
                "Technology", "Telecom", "Textile", "Tobacco", 
                "Water"]


def clear_last_run(pattern: str = "stocks-[\dQ]+\.json") -> None:
    """Removes all logging JSON files (matching the provided pattern)
        from the last time the model was run."""
    for file in os.listdir():
        if re.match(pattern, file):
            os.remove(file)


def get_latest_data() -> str:
    """Get the "latest" data (e.g., from our internal company service),
        as a JSON-serialized list of objects"""
    data = []
    for index in range( random.randint(3, 6) ):
        # keys are based on parameter names in the AL model
        # omitted entries will use the agent's default value
        entry = {
            "name": f"{random.choice(COMPANY_TYPES)}Company#{index}",
            ## "initialPrice": 0.5,
            "volatility": random.triangular(2, 10, 5)
            }
        data.append(entry)

    return json.dumps(data)


def save_latest_data(filename: str) -> None:
    """Get the "latest" data (e.g., from our internal company service),
        and save it to the specified local JSON file"""
    output = get_latest_data()
    with open(filename, "w") as outfile:
        outfile.write(output)
