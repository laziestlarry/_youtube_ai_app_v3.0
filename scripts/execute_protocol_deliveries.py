import asyncio
import sys
import os
from unittest.mock import AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.direction_board import direction_board
from modules.ai_agency.chimera_engine import chimera_engine
from modules.ai_agency.fulfillment_engine import fulfillment_engine

async def run_protocol_deliveries():
    print("🚀 EXECUTING ALEXANDRIA PROTOCOL DELIVERIES")
    print("===========================================")
    print("Targeting 'Estimated Numbers as Min' via Agency Fulfillment...\n")

    # Mock Chimera for speed/reliability
    chimera_engine.generate_response = AsyncMock(return_value="[PROTOCOL EXECUTION] Agency Agent deploying asset...")

    # Define the Protocol Deliveries (Tier 1 Assets)
    deliveries = [
        {
            "name": "Fiverr Gig System",
            "objective": "Execute Fiverr Gig System (high_ticket) - Bulk Order Processing",
            "dept": "operations", 
            "target": "$500+"
        },
        {
            "name": "ZentromaX Art Launch",
            "objective": "Execute ZentromaX Art Sale (launch_event) - Release Top 50 Collection",
            "dept": "operations",
            "target": "$500+"
        },
        {
            "name": "YouTube AI Platform",
            "objective": "Execute YouTube Platform Launch (high_ticket) - Initial Ad Revenue Spike",
            "dept": "operations",
            "target": "$2,000+"
        }
    ]

    total_generated = 0.0

    for item in deliveries:
        print(f"📦 Delivering Asset: {item['name']}...")
        print(f"   Objective: {item['objective']}")
        print(f"   Target Min: {item['target']}")
        
        result = await direction_board.execute_workflow(item['objective'], item['dept'])
        
        if result.get("status") == "completed":
            # Extract earnings from result string or query engine directly?
            # Let's query the engine for the latest transaction to fail-safe
            # (In a real app, result object should contain the structured data, 
            # but we baked it into the message string in previous step for simplicity)
            
            # Parsing the earnings from the message string:
            # "... (Earnings: $123.45)"
            msg = result.get("result", "")
            try:
                import re
                match = re.search(r"Earnings: \$([\d\.]+)", msg)
                if match:
                    amount = float(match.group(1))
                    total_generated += amount
                    print(f"   ✅ SUCCESS. Generated: ${amount:.2f}")
                else:
                    print(f"   ⚠️  Task executed but earnings parse failed. Msg: {msg}")
            except Exception as e:
                print(f"   ❌ Error parsing earnings: {e}")
                
        else:
             print(f"   ❌ FAILURE: {result}")
        print("   -----------------------------------")

    print("\n💰 FINAL PROTOCOL REPORT")
    print("========================")
    print(f"Total Value Delivered: ${total_generated:.2f}")
    
    if total_generated > 3000:
        print("✅ MISSION SUCCESS: Min Estimated Numbers ($3,000) Exceeded.")
    elif total_generated > 1000:
        print("⚠️  PARTIAL SUCCESS: Significant revenue, but below total min estimate.")
    else:
        print("❌ MISSION FAILED: Did not hit minimum targets.")

if __name__ == "__main__":
    asyncio.run(run_protocol_deliveries())
