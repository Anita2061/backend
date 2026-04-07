import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

local_uri = "mongodb://localhost:27017"

def test_uri(uri, name):
    print(f"Testing {name}...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print(f"{name} worked!")
        return True
    except PyMongoError as e:
        print(f"{name} failed: {e}")
        return False

test_uri(local_uri, "Local MongoDB")
