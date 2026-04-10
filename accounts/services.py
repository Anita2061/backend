from datetime import datetime, timezone

import bcrypt
from bson import ObjectId

from core.mongo import carts_collection, serialize_mongo_doc, user_collection, orders_collection


def create_order(user_id: str, items: list[dict], name: str, phone: str, location: str, total: float):
    order_data = {
        "user_id": user_id,
        "items": items,
        "shipping_details": {
            "name": name,
            "phone": phone,
            "location": location
        },
        "total": total,
        "status": "pending",
        "created_at": _now()
    }
    result = orders_collection.insert_one(order_data)
    
    # Note: Cart clearing is now handled by the frontend/caller 
    # to support partial item selection.
    
    order_data["_id"] = str(result.inserted_id)
    return serialize_mongo_doc(order_data)


def _now():
    return datetime.now(timezone.utc)

def get_user_by_id(user_id: str):
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    user = user_collection.find_one({"_id": oid})
    if not user:
        return None
    user.pop("password_hash", None)
    return serialize_mongo_doc(user)

def create_user_in_mongo(name: str, email: str, password: str, django_id: str):
    existing = user_collection.find_one({"email": email.lower().strip()})
    if existing:
        raise ValueError("Email already registered")

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_data = {
        "django_id": django_id,
        "name": name.strip(),
        "email": email.lower().strip(),
        "password_hash": pw_hash,
        "created_at": _now(),
    }
    result = user_collection.insert_one(user_data)
    created = user_collection.find_one({"_id": result.inserted_id}, {"password_hash": 0})
    carts_collection.update_one(
        {"user_id": django_id},
        {"$setOnInsert": {"user_id": django_id, "items": [], "updated_at": _now()}},
        upsert=True,
    )
    return serialize_mongo_doc(created)


def verify_user_credentials(email: str, password: str):
    user = user_collection.find_one({"email": email.lower().strip()})
    if not user:
        return None
    pw_hash = user.get("password_hash", "")
    if not pw_hash:
        return None
    ok = bcrypt.checkpw(password.encode("utf-8"), pw_hash.encode("utf-8"))
    if not ok:
        return None
    user.pop("password_hash", None)
    return serialize_mongo_doc(user)

def get_cart(user_id: str):
    cart = carts_collection.find_one({"user_id": user_id}) or {"user_id": user_id, "items": []}
    cart.pop("_id", None)
    return cart


def set_cart(user_id: str, items: list[dict]):
    carts_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "updated_at": _now()}},
        upsert=True,
    )
    return get_cart(user_id)

def get_all_users():
    users = list(user_collection.find({}, {"password_hash": 0}))
    return [serialize_mongo_doc(u) for u in users]