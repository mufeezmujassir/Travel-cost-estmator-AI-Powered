from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DATABASE_NAME")]
travel_plans_collection = db["travel_plans"]

# Helpful indexes
travel_plans_collection.create_index([("userId", 1), ("generated_at", -1)])
travel_plans_collection.create_index("request_id", unique=True)


