"""
Simple script to fill missing `phone` fields in `mappings` collection.
Run with: `python scripts/fill_missing_phone.py`
It reads MONGO_URI from environment (.env via config.py) and sets empty string for docs missing `phone`.
"""
import os
from pymongo import MongoClient
from config import Config

MONGO_URI = os.getenv('MONGO_URI') or Config.MONGO_URI
if not MONGO_URI:
    print("MONGO_URI not configured. Set it in environment or .env file.")
    exit(1)

client = MongoClient(MONGO_URI)
db = client.get_default_database()
collection = db.get_collection('mappings')

result = collection.update_many(
    {"$or": [{"phone": {"$exists": False}}, {"phone": None}]},
    {"$set": {"phone": ""}}
)

print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
client.close()