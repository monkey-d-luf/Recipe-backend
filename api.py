from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os

app = FastAPI()

# Allow React frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = MongoClient(os.getenv("MONGO_URI"))
# client = MongoClient("mongodb://localhost:27017/")
db = client["recipe_db"]
collection = db["recipes"]

# pagination endpoint

@app.get("/api/recipes")
def get_recipes(
    search: str = "",
    cuisine: str = None,
    min_rating: float = None,
    max_time: float = None,
    page: int = 1,
    limit: int = 10
):
    query = {}

    # 🔎 search by title (case insensitive)
    if search:
        query["title"] = {"$regex": search, "$options": "i"}

    # 🍽 filter by cuisine
    if cuisine:
        query["cuisine"] = cuisine

    # ⭐ minimum rating
    if min_rating is not None:
        query["rating"] = {"$gte": min_rating}

    # ⏱ maximum total time
    if max_time is not None:
        query["total_time"] = {"$lte": max_time}

    skip = (page - 1) * limit

    total = collection.count_documents(query)

    recipes = list(
        collection.find(query)
        .sort("rating", -1)
        .skip(skip)
        .limit(limit)
    )

    for r in recipes:
        r["_id"] = str(r["_id"])

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": recipes
    }

#search endpoint
@app.get("/api/recipes/search")
def search_recipes(
    title: str = None,
    cuisine: str = None,
    rating: float = None,
    total_time: float = None
):

    query = {}

    if title:
        query["title"] = {"$regex": title, "$options": "i"}

    if cuisine:
        query["cuisine"] = cuisine

    if rating:
        query["rating"] = {"$gte": rating}

    if total_time:
        query["total_time"] = {"$lte": total_time}

    recipes = list(collection.find(query))

    for r in recipes:
        r["_id"] = str(r["_id"])

    return {"data": recipes}
