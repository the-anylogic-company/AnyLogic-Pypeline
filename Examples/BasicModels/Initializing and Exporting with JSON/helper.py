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
    
def linear_regression(x, y):
    # Calculate the mean of X and Y
    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)

    # Calculate the differences between each X and the mean of X, and each Y and the mean of Y
    x_diff = [i - x_mean for i in x]
    y_diff = [i - y_mean for i in y]

    # Calculate the slope (m)
    m = sum([x_diff[i] * y_diff[i] for i in range(len(x))]) / sum([i**2 for i in x_diff])

    # Calculate the intercept (b)
    b = y_mean - m * x_mean

    # Print the results
    print("Slope (m):", m)
    print("Intercept (b):", b)
