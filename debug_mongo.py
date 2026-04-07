import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

uri1 = "mongodb+srv://anitagyawali101_db_user:PbzX7J90SU8OEuQr@cluster0.l5ckegz.mongodb.net/?appName=Cluster0"
uri2 = "mongodb+srv://anitagyawali101_db_user:PbzX7J90SU8OEuQr@cluster0.l5ckegz.mongodb.net/project_db?retryWrites=true&w=majority"

def test_uri(uri, name):
    print(f"Testing {name}...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"{name} worked!")
        return True
    except PyMongoError as e:
        print(f"{name} failed: {e}")
        return False

test_uri(uri1, "Original URI")
test_uri(uri2, "Revised URI")
