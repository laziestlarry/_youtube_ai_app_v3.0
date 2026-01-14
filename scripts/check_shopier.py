import os
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from backend.services.shopier_api_service import ShopierApiService

def main():
    # Load from .env.shopier manually since os.environ hasn't been updated
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
    
    print("Checking Shopier Products...")
    products = service.list_products()
    
    if products:
        print(f"Found {len(products)} products.")
        import json
        print(json.dumps(products[0], indent=2))
        for p in products:
            # Shopier API v1 might use different keys like 'title' or 'amount'
            name = p.get('name') or p.get('title') or "Unknown"
            price = p.get('price') or p.get('amount') or "0"
            print(f"- {name} (Price: {price})")
    else:
        print("No products found on Shopier.")

if __name__ == "__main__":
    main()
