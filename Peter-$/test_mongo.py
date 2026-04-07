from pymongo import MongoClient

# Replace with your .env MONGODB_URL value
MONGODB_URL = "mongodb+srv://admin:e@peter.zx2mihg.mongodb.net/peter?retryWrites=true&w=majority"

if not MONGODB_URL:
    raise ValueError("Missing MONGODB_URL!")

client = MongoClient(MONGODB_URL)

try:
    # Connect to the database
    db = client["AAT"]  # Replace "AAT" with your database name (if different)
    print("Connected successfully!")
    print("Collections:", db.list_collection_names())
except Exception as e:
    print("Failed to connect to MongoDB:", e)