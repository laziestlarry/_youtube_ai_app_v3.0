"""
Global Revenue Sync - Bridges youtube_ai.db (RevenueEvent) -> growth_engine.db (GrowthLedgerEntry).
Ensures all detected 'real' income is officially realized in the financial truth.
"""
import sys
import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

def sync():
    print("🚀 [GLOBAL SYNC] Initiating Financial Reconciliation...")
    
    data_dir = Path(os.getenv("DATA_DIR", ".")).resolve()
    youtube_url = os.getenv("DATABASE_URL", "")
    growth_url = os.getenv("GROWTH_DATABASE_URL", "")

    def _sqlite_path(url: str, fallback: Path) -> Path:
        if url.startswith("sqlite:///"):
            return Path(url.replace("sqlite:///", "")).resolve()
        return fallback

    YOUTUBE_DB = _sqlite_path(youtube_url, data_dir / "youtube_ai.db")
    GROWTH_DB = _sqlite_path(growth_url, data_dir / "growth_engine.db")
    
    if not YOUTUBE_DB.exists() or not GROWTH_DB.exists():
        print("❌ Error: One or both databases are missing.")
        return

    # 1. Fetch pending events from YouTube AI Discovery DB
    conn_yt = sqlite3.connect(str(YOUTUBE_DB))
    cursor_yt = conn_yt.cursor()
    
    try:
        # We target real and fiverr events
        cursor_yt.execute("SELECT id, amount, currency, source, kind, metadata_json, occurred_at FROM revenue_events WHERE kind != 'simulated'")
        events = cursor_yt.fetchall()
        print(f"📊 Detected {len(events)} candidate events in Discovery layer.")
    finally:
        conn_yt.close()

    if not events:
        print("✅ No pending real events to sync.")
        return

    # 2. Ingest into Growth Engine Ledger
    conn_gr = sqlite3.connect(str(GROWTH_DB))
    cursor_gr = conn_gr.cursor()
    
    synced_count = 0
    skipped_count = 0
    total_value = 0.0
    
    try:
        for event in events:
            yt_id, amount, currency, source, kind, metadata_raw, occurred_at = event
            
            # Map transaction ID - prioritize order_id from metadata if present
            meta = {}
            if metadata_raw:
                try:
                    meta = json.loads(metadata_raw)
                except:
                    pass
            
            transaction_id = meta.get("order_id") or f"discovery_{yt_id}"
            
            # Check for existing entry
            cursor_gr.execute("SELECT id FROM growth_ledger_entries WHERE transaction_id = ?", (transaction_id,))
            if cursor_gr.fetchone():
                skipped_count += 1
                continue
            
            # Record SKU or Source details in provenance
            provenance = {
                "origin_name": source,
                "origin_type": kind,
                "discovery_id": yt_id,
                "sync_time": datetime.now().isoformat(),
                "quality_score": 1.0
            }
            
            # Mapping stream logic
            stream = "POD"
            if kind == "fiverr_cooperation":
                stream = "CONTENT"
            elif "affiliate" in kind.lower():
                stream = "AFFILIATE"
            
            amount_cents = int(float(amount) * 100)
            
            # Insert into Master Ledger
            cursor_gr.execute("""
                INSERT INTO growth_ledger_entries (transaction_id, stream, amount_cents, currency, status, provenance_meta, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                stream,
                amount_cents,
                currency,
                "CLEARED",
                json.dumps(provenance),
                occurred_at,
                occurred_at
            ))
            
            synced_count += 1
            total_value += float(amount)
            print(f"   [SYNCED] {transaction_id} | ${amount:.2f} | {stream}")
            
        conn_gr.commit()
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        conn_gr.rollback()
    finally:
        conn_gr.close()

    print(f"\n✅ RECONCILIATION COMPLETE:")
    print(f"   - Total Synced: {synced_count}")
    print(f"   - Total Skipped: {skipped_count} (Duplicates)")
    print(f"   - Value Realized: ${total_value:.2f}")

if __name__ == "__main__":
    sync()
