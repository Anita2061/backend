import os
import sys

# Add backend dir to Python path
sys.path.append(r"c:\Users\New Panthi Traders\Desktop\Project.p\project\Backend")

from core.mongo import get_db_status, client

print("Testing MongoDB Connection...")
try:
    status = get_db_status()
    print("DB Status:", status)
except Exception as e:
    print("Exception occurred:", type(e).__name__, str(e))
