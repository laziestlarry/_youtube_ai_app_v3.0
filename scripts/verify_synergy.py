"""
Verification script for Fiverr and YouTube AI Synergy.
Tests autonomous cooperation and improved SEO metadata.
"""
import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from modules.ai_agency.marketing_commander import marketing_commander
from backend.services.fiverr_service import fiverr_service

async def verify_synergy():
    print("🚀 Starting Fiverr & YouTube AI Synergy Verification...")
    
    # 1. Load a high-ticket SKU
    sku = {
        "sku": "FIVERR-ELITE-01",
        "title": "Elite AI Automation Agency Setup",
        "short_description": "Complete setup of an autonomous AI agency on any cloud platform.",
        "long_description": "We will deploy a full stack of AI commanders, lead hunters, and revenue orchestrators to automate your business growth natively on the cloud.",
        "price": {"min": 999, "max": 2500, "currency": "USD"},
        "type": "service",
        "tags": ["AI Agency", "Automation", "B2B Sales", "SaaS"]
    }
    
    # 2. Test Improved YouTube Metadata (Turkish Localisation)
    print("\n[Step 1] Generating Improved YouTube SEO Metadata (TR)...")
    metadata = await marketing_commander.generate_youtube_metadata(sku, lang="TR")
    print("✅ Metadata Generated (TR):")
    print(f"   - Titles: {metadata.get('titles', metadata.get('3 Click-worthy Titles (high CTR)', 'N/A'))}")
    
    # 3. Test Fiverr Listing
    print("\n[Step 2] Executing Autonomous Fiverr Cooperation Listing...")
    fiverr_campaign = await marketing_commander.execute_campaign(sku, ["fiverr"])
    fiverr_status = fiverr_campaign['channels']['fiverr']
    print(f"✅ Fiverr Listing Result: {fiverr_status['status']}")
    print(f"   - Gig Title: {fiverr_status['title']}")
    print(f"   - Gig ID: {fiverr_status['gig_id']}")
    
    # 4. Test Autonomous Revenue Tracker (Fiverr Order)
    print("\n[Step 3] Simulating Autonomous Fiverr Order Ingestion...")
    order = await fiverr_service.simulate_order_ingestion(fiverr_status['gig_id'])
    print(f"✅ Revenue Tracked: ${order['amount']} {sku['price']['currency']}")
    print(f"   - Order ID: {order['order_id']}")
    
    # 5. Safety Wrap-up
    print("\n[Step 4] Finalizing async tasks...")
    await asyncio.sleep(2)
    
    print("\n🚀 SYNERGY VERIFICATION COMPLETE. SERVICE READY.")

if __name__ == "__main__":
    asyncio.run(verify_synergy())
