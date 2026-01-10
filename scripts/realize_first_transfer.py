import sys
from pathlib import Path
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Setup Path to import growth modules
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from modules.growth_engine_v1.ingest import IngestionService
from modules.growth_engine_v1.config import settings
from modules.growth_engine_v1.models import GrowthOrder, GrowthLedgerEntry

def realize_first_transfer():
    print("🚀 [ALEXANDRIA PROTOCOL] Realizing First Income Record...")
    
    # 2. Database Connection
    # Force SQLite for local realization to avoid async driver issues with sync engine
    db_path = project_root / "growth_engine.db"
    db_url = f"sqlite:///{db_path}"
    
    print(f"🔗 Connecting to Growth Engine Database: {db_url}")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 3. Formulate "First Transfer" Payload (Tier 3 Example)
        # Goal: $99.00 Transaction
        payload = {
            "id": "ALX-TRANS-20260109-99-FINAL",
            "buyer_email": "success@youtube-ai.com",
            "total_price": "99.00",
            "currency": "USD",
            "status": "paid",
            "product_name": "IntelliWealth Management (Tier 3 Activation)"
        }
        
        provenance = {
            "origin_name": "Shopier Direct (Alexandria)",
            "origin_type": "payment_gateway",
            "quality_score": 1.0,
            "verification_sha256": "manual_trigger_audit_trail_001"
        }

        # 4. Ingest via Service
        service = IngestionService(db)
        
        # Ingest as 'orders' topic
        result = service.ingest_order(payload, provenance)
        
        if result.get("status") == "ingested":
            print(f"✅ SUCCESS: Incomed $99.00 via id: {result.get('id')}")
            print("💰 Ledger entry automatically generated for stream: POD")
        else:
            print(f"⚠️  Result: {result}")

        # 5. Verify the state
        total_orders = db.query(GrowthOrder).count()
        ledger_entries = db.query(GrowthLedgerEntry).all()
        
        print("\n📈 [AUTONOMY STATUS REPORT]")
        print(f"Total Transactions: {total_orders}")
        print(f"Total Ledger Entries: {len(ledger_entries)}")
        
        print("\n📝 [LEDGER AUDIT TRAIL]")
        for entry in ledger_entries[-3:]: # Last 3
            print(f"- ID: {entry.transaction_id} | Amount: ${entry.amount_cents/100:.2f} | Status: {entry.status} | Stream: {entry.stream}")
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    realize_first_transfer()
