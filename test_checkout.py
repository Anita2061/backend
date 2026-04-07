import requests
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

user = get_random_string(8)
# Test order data
data = {
    "items": [{"productId": 3, "title": "Midnight Mascara", "price": 14.0, "qty": 1}],
    "name": "Test User",
    "phone": "123456789",
    "location": "Test Location",
    "total": 14.0
}

# Base URL
base = "http://127.0.0.1:8000/api/accounts"

try:
    r = requests.post(f"{base}/signup/", json={
        "username": user,
        "email": f"{user}@example.com",
        "password": "password123"
    })
    print(f"Signup: {r.status_code}")
    
    r = requests.post(f"{base}/login/", json={
        "username": user,
        "password": "password123"
    })
    print(f"Login: {r.status_code}")
    token = r.json().get("access")
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{base}/checkout/", json=data, headers=headers)
    print(f"Checkout: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 201:
        print("Test passed! Checkout successful with local MongoDB.")
    else:
        print("Test failed! Still getting error.")
except Exception as e:
    print(f"Test failed: {e}")
