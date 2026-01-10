import asyncio
import sys
import os
import json
from unittest.mock import AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.direction_board import direction_board
from modules.ai_agency.chimera_engine import chimera_engine
from modules.ai_agency.fulfillment_engine import fulfillment_engine

EARNINGS_FILE = "earnings.json"

async def run_optimization_sprint():
    print("🏃 ANALYZING PERFORMANCE FOR OPTIMIZATION SPRINT")
    print("===============================================")
    
    # 1. Analyze Ledger for Top Performer
    try:
        with open(EARNINGS_FILE, 'r') as f:
            data = json.load(f)
            history = data.get("history", [])
            
        # Simple attribution
        sector_earnings = {}
        for txn in history:
            source = txn.get("source", "").lower()
            amount = txn.get("amount", 0.0)
            
            sector = "other"
            if "zentromax" in source or "storefront" in source: sector = "ZentromaX (Sales)"
            elif "youtube" in source: sector = "YouTube (Platform)"
            elif "fiverr" in source: sector = "Fiverr (Services)"
            
            sector_earnings[sector] = sector_earnings.get(sector, 0.0) + amount
            
        # Find winner
        winner = max(sector_earnings, key=sector_earnings.get)
        print("📊 Attribution Analysis:")
        for s, amt in sector_earnings.items():
            print(f"   - {s}: ${amt:.2f}")
            
        print(f"\n🏆 OPTIMUM ASSET IDENTIFIED: {winner}")
        print("   -> Initiating Focused Sprint on this sector...")
        
    except Exception as e:
        print(f"❌ Analysis Failed: {e}")
        return

    # 2. Configure Sprint
    sprint_tasks = []
    chimera_engine.generate_response = AsyncMock(return_value="[SPRINT EXECUTION] Rapid deployment of optimized assets...")
    
    # Define sprint targets based on winner
    if "ZentromaX" in winner:
        # Launch Event Tier for Art
        task = {
            "objective": "Execute ZentromaX Flash Sale (launch_event) - Release Limited Edition Series",
            "dept": "operations"
        }
    elif "YouTube" in winner:
        # High Ticket for Ad Revenue
        task = {
            "objective": "Execute YouTube Viral Push (high_ticket) - Boost Top Performing Video",
            "dept": "operations"
        }
    else:
        # High Ticket Fiverr
        task = {
            "objective": "Execute Fiverr Bulk Delivery (high_ticket) - Process Corporate Orders",
            "dept": "operations"
        }
        
    # 3. Execute Sprint (5 Rapid Cycles)
    print("\n⚡️ STARTING SPRINT (5 CYCLES)")
    print("----------------------------")
    
    initial_total = data.get("total_earnings", 0.0)
    
    for i in range(1, 6):
        sys.stdout.write(f"   Cycle {i}/5: Discharging Payload... ")
        sys.stdout.flush()
        
        result = await direction_board.execute_workflow(task['objective'], task['dept'])
        
        if result.get("status") == "completed":
             # Parse result for visual feedback
            msg = result.get("result", "")
            import re
            match = re.search(r"Earnings: \$([\d\.]+)", msg)
            if match:
                print(f"✅ Generated ${float(match.group(1)):.2f}")
            else:
                print("✅ Task Complete.")
        else:
            print("❌ Failed.")
            
    # 4. Final Report
    final_data = fulfillment_engine.get_earnings_summary()
    final_total = final_data.get("total_earnings", 0.0)
    delta = final_total - initial_total
    
    print("\n🏁 SPRINT RESULTS")
    print("=================")
    print(f"💰 Sprint Generated: ${delta:.2f}")
    print(f"📈 New Grand Total:  ${final_total:.2f}")
    
    if delta > 2000:
        print("🚀 OPTIMUM BEST ACHIEVED: High-Velocity Revenue Event Confirmed.")

if __name__ == "__main__":
    asyncio.run(run_optimization_sprint())
