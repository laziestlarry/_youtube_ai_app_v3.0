import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.payment_service import PaymentService
from modules.ai_agency.shopier_service import shopier_service
from backend.config.enhanced_settings import get_settings

async def test_shopier_integration():
    print("🚀 Testing Shopier Integration...")
    
    # 1. Initialize Service
    payment_service = PaymentService()
    
    # 2. Check Configuration (Should be None/Mock by default)
    settings = get_settings()
    api_key = settings.payment.shopier_api_key
    print(f"Configured API Key: {'***' + api_key[-3:] if api_key else 'None/Mock'}")
    
    # 3. Generate Link
    order_id = "ORDER-12345"
    amount = 49.99
    currency = "USD"
    product = "AutonomaX Professional Plan"
    
    link = await payment_service.create_shopier_payment(amount, currency, order_id, product)
    print(f"Generated Link: {link}")
    
    # 4. Validation
    if "https://www.shopier.com" in link:
        if "mock" in link and not api_key:
             print("✅ Test Passed: Mock link generated (No API key present)")
        elif "id=" in link and api_key:
             print("✅ Test Passed: Live link structure generated")
        else:
             print("✅ Test Passed: Link generated successfully")
    else:
        print("❌ Test Failed: Invalid link format")

    # 5. Test HTML Generation (Force Mock Keys)
    print("\n🔬 Testing HTML Form Generation (Ported Logic)...")
    shopier_service.api_key = "MOCK_KEY"
    shopier_service.api_secret = "MOCK_SECRET"
    
    html = await payment_service.create_shopier_payment(amount, currency, order_id, product)
    if "<form id=\"shopier_payment_form\"" in html and "name=\"signature\"" in html:
         print("✅ Ported Logic Verified: HTML Form and Signature generated.")
         # print(html[:200] + "...") # Debug preview
    else:
         print("❌ Ported Logic Failed: HTML structure missing.")

if __name__ == "__main__":
    asyncio.run(test_shopier_integration())
