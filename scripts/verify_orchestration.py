import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.direction_board import direction_board

async def verify_orchestration():
    print("🎬 Verifying Dual Pipeline Orchestration")
    print("=======================================")

    # 1. Test Sales Department: Inventory Audit
    print("\n📦 Testing Sales Dept: Inventory Audit...")
    result_audit = await direction_board.execute_sales_operation("audit_inventory")
    if result_audit.get("status") == "success":
        print(f"   ✅ Audit Successful. Item Count: {result_audit.get('inventory_count')}")
    else:
        print(f"   ❌ Audit Failed: {result_audit}")

    # 2. Test Sales Department: Deploy Storefront
    print("\n🏗️  Testing Sales Dept: Deploy Storefront...")
    result_deploy = await direction_board.execute_sales_operation("deploy_storefront")
    if result_deploy.get("status") == "success":
        print("   ✅ Deployment Triggered Successfully.")
        print("   📄 Output Log (Last 100 chars):")
        print(f"   ...{result_deploy.get('output', '')[-100:].strip()}")
    else:
        print(f"   ❌ Deployment Failed: {result_deploy}")

    # 3. Test Operations Department: Service Workflow
    print("\n⚙️  Testing Ops Dept: Service Workflow (Simulated)...")
    # Note: This will actually try to call Chimera. 
    # If no LLM is running, it might timeout or fail. 
    # For this verification, we are checking the routing logic.
    try:
        # We can mock chimera_engine for this test to avoid real API calls
        from unittest.mock import AsyncMock
        from modules.ai_agency.chimera_engine import chimera_engine
        
        # Mocking generate_response
        chimera_engine.generate_response = AsyncMock(return_value="[MOCK PLAN] 1. Login to Fiverr. 2. Post Gig.")
        
        result_ops = await direction_board.execute_workflow(
            "Execute Fiverr Gig: Auto-Post 'AI Content Services'", 
            "operations"
        )
        
        if result_ops.get("status") == "completed" and "MOCK PLAN" in result_ops.get("result", ""):
            print("   ✅ Operations Task Routed & Executed (Mocked).")
            print(f"   📝 Plan: {result_ops.get('result')}")
        else:
             print(f"   ❌ Operations Task Failed: {result_ops}")

    except Exception as e:
        print(f"   ❌ Operations Test Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_orchestration())
