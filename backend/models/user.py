from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DATABASE_NAME")]
users_collection = db["users"]

# Create unique index for email
users_collection.create_index("email", unique=True)