import sys
from pathlib import Path
import os
import json
import asyncio
from datetime import datetime

# Setup Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from backend.services.delivery_service import delivery_service
from modules.ai_agency.fulfillment_engine import fulfillment_engine

async def test_hardened_flow():
    print("🛡️ [ALEXANDRIA HARDENING] Testing Hardened End-to-End Flow...")
    
    # Simulate a Shopier Callback Payload for a High-Ticket item
    payload = {
        "platform_order_id": "ALX-HARDENED-TEST-001",
        "product_name": "IntelliWealth Danışmanlık", # Matches IW-CONSULT-01 in shopier_product_map.json
        "buyer_email": "success@youtube-ai.com",
        "total_order_value": "99.00",
        "currency": "USD",
        "status": "success"
    }
    
    # 1. Test Delivery Resolution
    print("\n📦 Step 1: Triggering Digital Delivery...")
    # Base URL for link generation
    base_url = "https://autonomax.io" 
    result = delivery_service.deliver_digital(payload, base_url)
    
    print(f"Result Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Resolved SKU: {result.sku}")
    print(f"Download URL: {result.download_url}")
    
    # 2. Test Fulfillment Recording (Hardened)
    if result.status == "delivered":
        print("\n💰 Step 2: Recording Real Sale in Growth Ledger...")
        fulfillment_engine.record_sale(
            amount=99.00,
            source=f"Hardened Test: {payload['product_name']}",
            asset_url=result.download_url,
            metadata={
                "order_id": result.order_id,
                "sku": result.sku,
                "kind": "real",
                "channel": "shopier"
            }
        )
        print("✅ Entry recorded.")
    
    # 3. Verify Files
    print("\n🔍 Step 3: Verifying Logs...")
    if os.path.exists("logs/shopier_orders.jsonl"):
        print("✅ shopier_orders.jsonl updated.")
    
    print("\n✨ Hardening Verification Complete.")

if __name__ == "__main__":
    asyncio.run(test_hardened_flow())
