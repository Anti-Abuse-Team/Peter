import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()



mongodb = MongoClient(os.getenv("MONGODB_URL"))
db = mongodb["AAT"]
roles_db = db["roles"]
keys_db = db["keys"]

client = motor.motor_asyncio.AsyncIOMotorClient(
    os.getenv("MONGODB_URL"),
    compressors=['zlib'],
    maxPoolSize=150,
    minPoolSize=10,
    maxIdleTimeMS=300000,
    socketTimeoutMS=10000,
    connectTimeoutMS=10000,
    serverSelectionTimeoutMS=5000,
)

db = client['AAT']
roles = db["roles"]
