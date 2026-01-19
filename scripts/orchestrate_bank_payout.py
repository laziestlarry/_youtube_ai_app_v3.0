import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

# Respect configured DB; fallback to local SQLite when not provided.
if not os.getenv("GROWTH_DATABASE_URL"):
    data_dir = os.getenv("DATA_DIR", ".")
    os.environ["GROWTH_DATABASE_URL"] = f"sqlite:///{data_dir}/growth_engine.db"

from modules.growth_engine_v1.app import SessionLocal
from modules.growth_engine_v1.payout_service import PayoutService

async def run_payout_orchestration():
    print("🏦 AutonomaX: Bank Payout Orchestration")
    print("========================================")
    
    db = SessionLocal()
    service = PayoutService(db)
    
    print("📡 Scanning Ledger for Cleared Funds...")
    result = service.orchestrate_payout()
    
    if result["status"] == "initiated":
        print(f"🔥 PAYOUT INITIATED!")
        print(f"   - Reference: {result['payout_ref']}")
        print(f"   - Amount: ${result['total_amount']:.2f} USD")
        print(f"   - Entries Settled: {result['entry_count']}")
        print(f"   - Destination: {result['destination']}")
        print(f"   - Status: CONVERTED CLEARED LEDGER TO BANK TRANSFER")
    else:
        print(f"⚠️  No Cleared Funds: {result.get('reason')}")
        
    db.close()
    
    print("\n🏁 SETTLEMENT CYCLE COMPLETE")

if __name__ == "__main__":
    asyncio.run(run_payout_orchestration())
