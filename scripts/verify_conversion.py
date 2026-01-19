import asyncio
import logging
import json
from pathlib import Path
import sys

# Add project root to sys.path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

logging.basicConfig(level=logging.INFO)
from modules.ai_agency.marketing_commander import marketing_commander
from modules.ai_agency.lead_hunter import lead_hunter

async def verify_optimization():
    print("🚀 Verifying Conversion Optimization Layer...")
    
    # Test high-ticket SKU
    high_ticket_sku = {
        "sku": "IW-CONSULT-01",
        "title": "IntelliWealth Management Consulting",
        "short_description": "Enterprise-grade AI transformation and operations.",
        "long_description": "Distilled knowledge of the AutonomaX protocol for 7-figure scaling.",
        "price": {"min": 15000, "max": 50000},
        "type": "consulting",
        "tags": ["AI Consulting", "Enterprise", "B2B"]
    }
    
    print("\n--- Generating Optimized YouTube Script ---")
    script = await marketing_commander.generate_youtube_script(high_ticket_sku)
    print(f"Script Preview: {script[:200]}...")
    
    # Check for keywords
    roi_keywords = ["ROI", "investment", "return", "AutonomaX", "Alexandria", "Protocol"]
    found = [k for k in roi_keywords if k.lower() in script.lower()]
    print(f"ROI Keywords found: {found}")
    
    print("\n--- Generating Optimized Persona ---")
    persona = await lead_hunter.ideate_target_persona(high_ticket_sku, context="US Market Expansion")
    print(f"Persona: {json.dumps(persona, indent=2)}")

if __name__ == "__main__":
    asyncio.run(verify_optimization())
