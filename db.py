from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI missing in .env")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

client.admin.command("ping")

print("✅ MongoDB Connected Successfully")

# DATABASE

db = client["veridion_ai"]

# COLLECTIONS

users = db["users"]
chats = db["chats"]
otps = db["otps"]

print("✅ Collections Ready")