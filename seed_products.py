import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

load_dotenv(dotenv_path=backend_dir / ".env")

def get_product_data():
    frontend_data_path = backend_dir.parent / "src" / "data" / "Product.js"
    with open(frontend_data_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    products = []
    
    blocks = content.split('{')
    for block in blocks[1:]:
        if 'id:' in block and 'title:' in block:
            try:
                id_val = int(re.search(r'id:\s*(\d+)', block).group(1))
                title_val = re.search(r'title:\s*"([^"]+)"', block).group(1)
                category_val = re.search(r'category:\s*"([^"]+)"', block).group(1)
                price_val = float(re.search(r'price:\s*([\d.]+)', block).group(1))
                desc_val = re.search(r'description:\s*"([^"]+)"', block).group(1)
                image_match = re.search(r'image:\s*"([^"]+)"', block)
                image_val = image_match.group(1) if image_match else ""
                
                products.append({
                    "id": id_val,
                    "title": title_val,
                    "category": category_val,
                    "price": price_val,
                    "description": desc_val,
                    "image": image_val
                })
            except Exception as e:
                print(f"Failed to parse block: {e}")
                pass
    return products

def seed():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "project_db")
    
    if not mongo_uri:
        print("Error: MONGO_URI not found in .env")
        return

    client = MongoClient(mongo_uri)
    db = client[db_name]
    products_col = db["products"]
    
    # Clear existing products to avoid duplicates during seeding
    products_col.delete_many({})
    
    products = get_product_data()
    if products:
        result = products_col.insert_many(products)
        print(f"Successfully seeded {len(result.inserted_ids)} products into database '{db_name}'.")
    else:
        print("No products found to seed.")

if __name__ == "__main__":
    seed()
