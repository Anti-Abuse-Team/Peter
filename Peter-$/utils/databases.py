import pymongo
from pymongo import MongoClient
import os
import sys
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

# Validate MongoDB URL is configured
mongodb_url = os.getenv("MONGODB_URL")
if not mongodb_url:
    print("❌ ERROR: MONGODB_URL is not configured in your .env file!")
    print("   Please add 'MONGODB_URL=mongodb://localhost:27017' (or your MongoDB connection string) to your .env file.")
    sys.exit(1)

mongodb = MongoClient(mongodb_url)
db = mongodb["AAT"]
roles_db = db["roles"]
keys_db = db["keys"]

client = motor.motor_asyncio.AsyncIOMotorClient(
    mongodb_url,
    compressors=['zlib'],
    maxPoolSize=150,
    minPoolSize=10,
    maxIdleTimeMS=300000,
    socketTimeoutMS=10000,
    connectTimeoutMS=10000,
    serverSelectionTimeoutMS=5000,
)

db_async = client['AAT']
roles = db_async["roles"]
loa = db_async["loa"]  # LOA (Leave of Absence) tracking
