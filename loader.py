import json
from pymongo import MongoClient
import os

#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient(os.getenv("MONGO_URI"))
db = client["recipe_db"]
collection = db["recipes"]

def clean_numeric(value):
    if value in ["NaN", "", None]:
        return None
    try:
        return float(value)
    except:
        return None

def load_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    cleaned = []
    if isinstance(recipes, dict):
        recipes = list(recipes.values())

    for r in recipes:
        r["rating"] = clean_numeric(r.get("rating"))
        r["prep_time"] = clean_numeric(r.get("prep_time"))
        r["cook_time"] = clean_numeric(r.get("cook_time"))
        r["total_time"] = clean_numeric(r.get("total_time"))

        cleaned.append(r)

    collection.delete_many({})  # prevents duplicate inserts
    collection.insert_many(cleaned)

    print("Data inserted successfully!")

if __name__ == "__main__":
    load_data("US_recipes_null.json")
