import os
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from backend.services.shopier_api_service import ShopierApiService

def main():
    # Load token from .env.shopier
    token = None
    with open(".env.shopier", "r") as f:
        for line in f:
            if "SHOPIER_PERSONAL_ACCESS_TOKEN" in line:
                token = line.split("=")[1].strip().strip('"')
                break
    
    if not token:
        print("Token not found in .env.shopier")
        return

    os.environ["SHOPIER_PERSONAL_ACCESS_TOKEN"] = token
    service = ShopierApiService()
    
    product_id = "43225400"
    print(f"Updating stock for product: {product_id}...")
    
    # Try multiple keys to ensure the API accepts it
    update_data = {
        "stock": 9999,
        "stockQuantity": 9999,
        "stockStatus": "inStock"
    }
    
    try:
        result = service.update_product(product_id, update_data)
        print("Successfully updated!")
        import json
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    main()
