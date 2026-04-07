from pymongo import MongoClient
uri = 'mongodb+srv://<anitagyawali101_db_user>:<anita2026>@cluster0.l5ckegz.mongodb.net/'
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print('Connected to MongoDB')
except Exception as e:
    print('Connection error:', e)
