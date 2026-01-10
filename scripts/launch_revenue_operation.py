import sys
import os
import asyncio
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.payment_service import PaymentService
from backend.config.enhanced_settings import get_settings

async def launch_operation():
    print("\n🚀 LAUNCHING 'First Income' OPERATION")
    print("====================================")
    
    # 1. Define Product (Based on Ranked Opportunity #2)
    product_name = "ZentromaX Minimalist Digital Art Pack (130+ Assets)"
    price = 29.99
    currency = "USD"
    order_id = f"ZENTRO-{int(time.time())}"
    
    print(f"📦 Product Content: {product_name}")
    print(f"💰 Price Point: ${price} {currency}")
    
    # 2. Generate Payment Link
    print("\n... Generating Shopier Payment Gateway Link ...")
    payment_service = PaymentService()
    link = await payment_service.create_shopier_payment(price, currency, order_id, product_name)
    
    if not link:
        print("❌ Failed to generate payment link. Check configuration.")
        return

    print("\n✅ PAY HERE TO START REVENUE STREAM:")
    print(f"👉 {link}")
    
    # 3. Simulate Operation Loop
    print("\n... Operation Live. Listening for transactions (Simulated) ...")
    
    # Simulate a "waiting" period
    try:
        for i in range(1, 11):
            sys.stdout.write(f"\r⏳ Uptime: {i}s | Active Visitors: {random.randint(5, 50)}")
            sys.stdout.flush()
            await asyncio.sleep(1)
            
            # Simulate a "sale" (Mock)
            # if i == 5:
            #     print("\n\n🎉 NEW SALE DETECTED! +$29.99")
            #     print("   Buyer: customer@example.com")
            #     print("   Status: Fulfillment sent.")
    except KeyboardInterrupt:
        print("\n\n🛑 Operation stopped by user.")

    print("\n\n(Note: Add PAYMENT_SHOPIER_API_KEY to .env for real transactions)")

if __name__ == "__main__":
    asyncio.run(launch_operation())
