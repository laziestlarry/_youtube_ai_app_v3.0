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
    print(f"Checking status for product: {product_id}...")
    try:
        product = service.get_product(product_id)
        import json
        print(json.dumps(product, indent=2))
    except Exception as e:
        print(f"Failed to fetch product: {e}")

if __name__ == "__main__":
    main()
