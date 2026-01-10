import asyncio
import sys
import os
from unittest.mock import AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.direction_board import direction_board
from modules.ai_agency.chimera_engine import chimera_engine
from modules.ai_agency.fulfillment_engine import fulfillment_engine

async def verify_saas_launch():
    print("🚀 TARGETING TIER 2: SAAS PLATFORM LAUNCH")
    print("=========================================")
    
    # Mock Chimera
    chimera_engine.generate_response = AsyncMock(return_value="[SAAS LAUNCH] Activating platforms and onboarding first batch of users...")

    # Launch Objective
    objective = "Execute AutonomaX SaaS Beta Launch (launch_event) - Onboard Batch #001"
    
    print(f"📡 Triggering: {objective}")
    
    result = await direction_board.execute_workflow(objective, "operations")
    
    if result.get("status") == "completed":
        msg = result.get("result", "")
        import re
        match = re.search(r"Earnings: \$([\d\.]+)", msg)
        if match:
            amount = float(match.group(1))
            print(f"   ✅ LAUNCH SUCCESS. Initial MRR Contribution: ${amount:.2f}")
        else:
             print(f"   ⚠️  Launch executed (Log: {msg[:100]}...)")
    else:
        print(f"   ❌ Launch Failed: {result}")

    # Check Total
    data = fulfillment_engine.get_earnings_summary()
    print(f"\n📊 TOTAL AGENCY ASSET VALUE: ${data['total_earnings']:.2f}")

if __name__ == "__main__":
    asyncio.run(verify_saas_launch())
