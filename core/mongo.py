import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Create the client
_mongo_uri = os.getenv("MONGO_URI", "")
if not _mongo_uri:
    raise RuntimeError("MONGO_URI is not set. Add it to Backend/.env or your environment.")

client = MongoClient(_mongo_uri, serverSelectionTimeoutMS=5000, connect=False)

if client:
# Define the database
    db = client[os.getenv("MONGO_DB_NAME", "project_db")]

    # Define Collections
    user_collection = db["users"]
    products_collection = db["products"]
    orders_collection = db["orders"]
    carts_collection = db["carts"]

    print("User connected successfully")
else:
    print("Not connected")

def get_db_status():
    try:
        client.admin.command("ping")  # Forces a call to the server
        return True
    except PyMongoError as e:
        print(f"Connection failed: {e}")
        return False

from datetime import datetime

def serialize_mongo_doc(doc):
    """Convert Mongo types to JSON-friendly dict."""
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    
    if not isinstance(doc, dict):
        if isinstance(doc, datetime):
            return doc.isoformat()
        if isinstance(doc, (bytes, bytearray)):
            return str(doc)
        return doc

    new_doc = {}
    for key, value in doc.items():
        if key == "_id":
            new_doc[key] = str(value)
        elif isinstance(value, datetime):
            new_doc[key] = value.isoformat()
        elif isinstance(value, dict):
            new_doc[key] = serialize_mongo_doc(value)
        elif isinstance(value, list):
            new_doc[key] = [serialize_mongo_doc(item) for item in value]
        else:
            new_doc[key] = value
    return new_doc
