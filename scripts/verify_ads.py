import asyncio
import logging
import json
from pathlib import Path
import sys

# Add project root to sys.path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

logging.basicConfig(level=logging.INFO)
from modules.ai_agency.revenue_orchestrator import revenue_orchestrator

async def verify_ads_scaling():
    print("🚀 Verifying Autonomous Ads Scaling...")
    
    # Test high-ticket SKU for Ads
    high_ticket_sku = {
        "sku": "CMD-API-01",
        "title": "Commander API Operations",
        "short_description": "Direct autonomous API integration for enterprise scale.",
        "long_description": "Unlock 1,000+ autonomous agents with low-latency API access.",
        "price": {"min": 2000, "max": 9999},
        "type": "saas",
        "tags": ["API", "Automation", "Enterprise", "B2B"]
    }
    
    print("\n--- Executing Ads Sprint ---")
    ads_pack = await revenue_orchestrator.execute_ads_sprint(high_ticket_sku)
    
    print(f"\nSKU: {ads_pack['sku']}")
    print(f"Platform: {ads_pack['ad_variations']['platform']}")
    print(f"BudgetTarget: ${ads_pack['ad_variations']['suggested_daily_budget']}/day")
    
    print("\n--- Ad Variations Output ---")
    print(ads_pack['ad_variations']['variations'])
    
    print("\n--- Targeting Strategy Preview ---")
    print(ads_pack['targeting_strategy']['targeting_suggestions'])
    
    if ads_pack['ready_for_deploy']:
        print("\n✅ Ads Sprint Verified: Ready for production deployment.")

if __name__ == "__main__":
    asyncio.run(verify_ads_scaling())
