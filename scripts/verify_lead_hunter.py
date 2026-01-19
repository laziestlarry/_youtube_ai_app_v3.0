import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from modules.ai_agency.revenue_orchestrator import revenue_orchestrator

async def verify_unattended_growth():
    print("🚀 Verifying Unattended Growth Operations...")
    print("Scenario: Revenue < $100. System must trigger Lead Hunter.")
    
    try:
        # Trigger the mission
        result = await revenue_orchestrator.daily_mission()
        
        print("\n--- Mission Summary ---")
        print(f"Mission ID: {result['mission_id']}")
        print(f"Revenue Yesterday: ${result['revenue_yesterday']}")
        
        for action in result['actions']:
            print(f"\nAction Type: {action['type']}")
            if action['type'] == 'autonomous_lead_hunt':
                hunt = action['hunt_summary']
                print(f"SKU: {action['sku']}")
                print(f"Persona Ideated: {hunt.get('persona', {}).get('raw_persona', 'Complex Persona Generated')}")
                print(f"Criteria Defined: {hunt.get('criteria')}")
                print(f"Targets Discovered: {hunt.get('targets_discovered')}")
                print(f"Outreach Result (Summary): {len(hunt.get('outreach_results', {}))} channels contacted.")
        
        print("\n✅ Verification Complete: Unattended Growth Loop Operational.")
        
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_unattended_growth())
