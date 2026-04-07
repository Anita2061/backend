from pymongo import MongoClient
try:
    client = MongoClient("mongodb://localhost:27017")
    db = client["project_db"]
    res = db["test"].insert_one({"test": "data"})
    print(f"Insert worked: {res.inserted_id}")
    db["test"].delete_one({"_id": res.inserted_id})
    print("Delete worked")
except Exception as e:
    print(f"Local test failed: {e}")
