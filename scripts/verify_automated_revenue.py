import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.fulfillment_engine import fulfillment_engine

async def verify_revenue_loop():
    print("💰 Verifying Automated Revenue Loop")
    print("===================================")

    # 1. Check Initial State
    initial_data = fulfillment_engine.get_earnings_summary()
    initial_total = initial_data.get("total_earnings", 0.0)
    print(f"📊 Initial Earnings: ${initial_total:.2f}")

    # 2. Simulate Work (e.g., Fiverr Gig)
    print("\n🛠️  Simulating Work: 'Complete Premium Fiverr Gig'...")
    from modules.ai_agency.direction_board import direction_board
    
    # We use DirectionBoard to route it, ensuring full integration
    # Mocking Chimera to avoid timeouts/costs
    from unittest.mock import AsyncMock
    from modules.ai_agency.chimera_engine import chimera_engine
    chimera_engine.generate_response = AsyncMock(return_value="[MOCK WORK] Executing gig requirements...")
    
    result = await direction_board.execute_workflow(
        "Complete Premium Fiverr Gig for Client X", 
        "operations"
    )
    
    if result.get("status") == "completed":
        print("   ✅ Work Task Completed.")
        print(f"   📝 Output: {result.get('result')[:100]}...")
    else:
        print(f"   ❌ Work Task Failed: {result}")
        return

    # 3. Verify Ledger Update
    final_data = fulfillment_engine.get_earnings_summary()
    final_total = final_data.get("total_earnings", 0.0)
    
    print(f"\n📊 Final Earnings: ${final_total:.2f}")
    
    earned = final_total - initial_total
    if earned > 0:
        print(f"   ✅ Revenue Generated: ${earned:.2f}")
        print("   ✅ Validated: Work -> Ledger Update Loop is Active.")
    else:
        print("   ❌ Error: No revenue generated from work.")

if __name__ == "__main__":
    asyncio.run(verify_revenue_loop())
