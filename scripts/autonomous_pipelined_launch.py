"""
Autonomous Pipelined Launch - The Orchestrator.
Iterates through all SKUs and triggers the full autonomous synergy loop.
"""
import asyncio
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.services.fiverr_service import fiverr_service
from modules.ai_agency.marketing_commander import marketing_commander

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def launch_pipeline():
    print("🎬 [PIPELINE] Initiating Orchestrated Job Load Launch...")
    
    # 1. Update Profile/Identity
    profile = {
        "username": "AutonomaX_Expert",
        "tagline": "AI-Driven YouTube Growth & Automation",
        "description": "I provide end-to-end autonomous YouTube channel management and growth systems powered by the Alexandria Protocol. Proud partner of TekraQual.com - delivering elite AI infrastructure for top-tier creators.",
        "avatar_url": "/static/assets/fiverr_profile_avatar.png"
    }
    await fiverr_service.update_seller_identity(profile)
    
    # 2. Add Showcase to Portfolio
    portfolio_items = [
        {
            "title": "YouTube AI Automation Dashboard",
            "description": "A glimpse into our high-velocity autonomous content engine.",
            "media_url": "/static/assets/fiverr_gig_showcase.png"
        },
        {
            "title": "TekraQual Elite Gift Asset",
            "description": "Exclusive high-authority partner access to tekraqual.com.",
            "media_url": "/static/assets/tekraqual_gift_showcase.png"
        }
    ]
    for item in portfolio_items:
        await fiverr_service.add_to_portfolio(item)
    
    # 3. Iterate SKUs and Launch
    catalog_path = "docs/commerce/product_catalog.json"
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    products = catalog.get('products', [])
    print(f"📦 [PIPELINE] Detected {len(products)} SKUs in pipeline.")
    
    launched_count = 0
    
    # Sort products to ensure the Golden Gift is launched first
    products.sort(key=lambda x: 0 if x['sku'] == 'TEKRAQUAL-GIFT-01' else 1)
    
    # Limit to top 6 for initial autonomous trigger (Gift + 5 others)
    for product in products[:6]:
        print(f"\n🚀 [LAUNCHING] {product['sku']} - {product['title']}")
        
        # A. Create Fiverr Gig with Creative Assets
        gig = await fiverr_service.create_gig_listing(product, media_assets=["/static/assets/fiverr_gig_showcase.png"])
        print(f"   - Gig Registered: {gig['gig_id']}")
        
        # B. Generate YouTube Meta & Content
        print("   - Generating SEO Content & Scripts...")
        metadata = await marketing_commander.generate_youtube_metadata(product)
        
        # C. Orchestrate Job Load (Team Communication Signal)
        load = await fiverr_service.orchestrate_job_load(gig['gig_id'], {"product": product})
        print(f"   📡 [NETWORK] Job Load Status: {load['status']} | Assignment: {load['agent_assignment']}")
        
        launched_count += 1
        await asyncio.sleep(1) # Interval for stability

    print(f"\n✅ PIPELINE FINALIZATION COMPLETE. {launched_count} SKU(s) Ignited.")

if __name__ == "__main__":
    asyncio.run(launch_pipeline())
