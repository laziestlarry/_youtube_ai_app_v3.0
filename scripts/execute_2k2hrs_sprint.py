import asyncio
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("2k2hrs_sprint")

from modules.ai_agency.revenue_orchestrator import revenue_orchestrator

async def run_sprint():
    print("\n" + "="*50)
    print("🚀 IGNITING 2K2HRS QUANTUM SPRINT")
    print("="*50)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: $2,000 USD")
    print("Window: 2 Hours")
    print("Intensity: EXTREME")
    print("="*50 + "\n")
    
    try:
        # Trigger the sprint mission
        result = await revenue_orchestrator.sprint_mission(target=2000.0, duration_hrs=2)
        
        print("\n--- Phase 1: High-Ticket Targeting & Intent Collapse ---")
        print(f"Sprint ID: {result['sprint_id']}")
        
        for action in result['actions']:
            if action['type'] == 'quantum_pulse_complete':
                print(f"✅ Pulse Complete: Targeted {action['targets_count']} high-ticket assets.")
                print(f"Summary: {action['execution_summary']}")
        
        print("\n--- Phase 2: Parallel Outreach Active ---")
        print("LinkedIn: Aggressively targeting decision-makers.")
        print("Twitter: Viral 'Proof-of-Value' cycles initiated.")
        print("Lead Hunter: Deep-search persona expansion operational.")
        
        print("\n" + "="*50)
        print("🔥 SPRINT ACTIVE: Monitor Growth Ledger for conversions.")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Sprint Ignition Failed: {e}")
        logger.error(f"Sprint failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_sprint())
