import asyncio
import sys
import os
import random
from unittest.mock import AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.direction_board import direction_board
from modules.ai_agency.chimera_engine import chimera_engine

async def run_marketing_simulation():
    print("📢 ACTIVATING MARKETING & SALES BOT")
    print("===================================")
    
    # Mock Chimera
    chimera_engine.generate_response = AsyncMock(return_value="[SALES AGENT] Engaging prospect for Profit OS...")

    campaigns = [
        "Execute LinkedIn Outreach for Profit OS (High Ticket) - Targeted CEO Scrape",
        "Execute Email Drip Campaign (Standard) - Retargeting Warm Leads"
    ]
    
    # Run Marketing -> Traffic
    for campaign in campaigns:
        print(f"📡 Running Campaign: {campaign}")
        # We route this through 'operations' which uses FulfillmentEngine
        # If the string contains "High Ticket" it simulates high value
        
        # Add 'consulting' keyword to trigger the specific logic in FulfillmentEngine
        obj = f"{campaign} - Objective: Close Consulting Deal"
        
        result = await direction_board.execute_workflow(obj, "operations")
        
        if result.get("status") == "completed":
             # Parse result for visual feedback
            msg = result.get("result", "")
            import re
            match = re.search(r"Earnings: \$([\d\.]+)", msg)
            if match:
                print(f"   ✅ CONVERSION! Revenue: ${float(match.group(1)):.2f}")
            else:
                print(f"   ⚠️  Traffic Generated (No immediate sale)")
        else:
            print("   ❌ Campaign Failed.")
            
    print("\n📈 Marketing Run Complete.")

if __name__ == "__main__":
    asyncio.run(run_marketing_simulation())
