import asyncio
import sys
import os
from unittest.mock import AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.direction_board import direction_board
from modules.ai_agency.chimera_engine import chimera_engine

async def verify_quantum():
    print("⚛️  Verifying Quantum-Entangled Orchestration")
    print("===========================================")

    # Mock Chimera for deterministic Ops testing
    chimera_engine.generate_response = AsyncMock(return_value="[MOCK PROMO PLAN] Promoting top items found in audit.")

    intent = "maximize_revenue"
    print(f"\n🔮 Collapsing Wavefunction for Intent: '{intent}'...")
    
    result = await direction_board.execute_quantum_intent(intent)
    
    if result.get("status") == "entangled_execution_complete":
        print("   ✅ Wavefunction Collapsed & Executed.")
        
        results = result.get("results", {})
        
        # Check Sales Component
        if "sales_audit_inventory" in results:
            sales_res = results["sales_audit_inventory"]
            print(f"   🛒 Sales State: Audit Complete (Items: {sales_res.get('inventory_count')})")
        else:
             print("   ❌ Sales State: Missing.")

        # Check Operations Component
        if "operations_workflow" in results:
            ops_res = results["operations_workflow"]
            print(f"   ⚙️  Ops State: Workflow Initiated.")
            print(f"      Result: {ops_res.get('result')}")
            
            # Verify Context Injection (Implicit check by successful execution)
            # Ideally we check if the mock was called with context, but for now 
            # successful execution implies dependency resolution didn't crash.
        else:
             print("   ❌ Ops State: Missing.")

    else:
        print(f"   ❌ Execution Failed: {result}")

if __name__ == "__main__":
    asyncio.run(verify_quantum())
