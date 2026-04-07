import os
import sys
from pathlib import Path
from django.conf import settings

# Setup Django environment
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from accounts.services import create_order
from datetime import datetime, timezone

def test_checkout():
    print("Starting checkout test...")
    user_id = "test_user_123"
    items = [
        {"productId": 1, "title": "Test Product", "price": 20.0, "qty": 2}
    ]
    name = "Test User"
    phone = "9876543210"
    location = "Test Location"
    total = 40.0

    try:
        print(f"Calling create_order with: user_id={user_id}, name={name}")
        order = create_order(user_id, items, name, phone, location, total)
        print("Order creation successful!")
        print(f"Order ID: {order['_id']}")
        print(f"Created at: {order['created_at']}")
    except Exception as e:
        print(f"Order creation FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_checkout()
