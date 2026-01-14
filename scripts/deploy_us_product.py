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
    
    # Define US-market product
    product_data = {
        "title": "Fiverr AI Automation and Content Services Kit",
        "description": ("The ultimate toolkit for high-value AI service providers."),
        "type": "digital",
        "price": 949.00,
        "currency": "TRY",
        "media": [
            {
                "type": "image",
                "url": "https://cdn.shopier.app/pictures_large/autonomax_1316da0f-fb0f-4d57-bdd2-ca7d17d83902.png",
                "placement": 1
            }
        ],
        "stock": 9999,
        "is_active": True
    }
    
    print(f"Deploying product to Shopier: {product_data['title']}...")
    try:
        result = service.create_product(product_data)
        print("Successfully deployed!")
        print(f"Product ID: {result.get('id')}")
        print(f"Product URL: https://www.shopier.com/{result.get('id')}")
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    main()
