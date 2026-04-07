from pymongo import MongoClient
uri = "mongodb://localhost:27017"
client = MongoClient(uri)
db = client["project_db"]
count = db["products"].count_documents({})
print(f"Products in local DB: {count}")
