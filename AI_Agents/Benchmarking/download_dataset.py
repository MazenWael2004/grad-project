from datasets import load_dataset
import pandas as pd

def download_dataset():
    dataset = load_dataset("osunlp/TravelPlanner", "train")
    df = pd.DataFrame(dataset)
    df.to_csv("travel_planner.csv", index=False)
    print("Dataset saved to travel_planner.csv")
    return df

if __name__ == "__main__":
    download_dataset()