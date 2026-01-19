"""
Growth Ledger Monitor - Consolidated Audit Script.
Checks both youtube_ai.db (RevenueEvent) and growth_engine.db (GrowthLedgerEntry).
"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime

def monitor():
    print(f"🕵️  [MONITOR] Scanning for Conversions ({datetime.now().isoformat()})\n")
    
    # 1. Audit Growth Engine Ledger (The Financial Truth)
    print("💎 [GROWTH ENGINE LEDGER] status:")
    data_dir = Path(os.getenv("DATA_DIR", ".")).resolve()
    growth_db = data_dir / "growth_engine.db"
    youtube_db = data_dir / "youtube_ai.db"

    if growth_db.exists():
        conn = sqlite3.connect(str(growth_db))
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*), SUM(amount_cents) FROM growth_ledger_entries")
            count, total_cents = cursor.fetchone()
            print(f"   - Total Entries: {count}")
            print(f"   - Total Revenue: ${total_cents/100:.2f}")
            
            cursor.execute("SELECT transaction_id, amount_cents, stream, created_at FROM growth_ledger_entries ORDER BY created_at DESC LIMIT 5")
            print("\n   [Latest Transactions]:")
            for row in cursor.fetchall():
                print(f"     - {row[3]} | {row[0]} | ${row[1]/100:.2f} | {row[2]}")
        except Exception as e:
            print(f"   - Error scanning growth_engine.db: {e}")
        finally:
            conn.close()
    else:
        print("   - growth_engine.db not found.")

    # 2. Audit Revenue Events (Ignition Layer)
    print("\n🔥 [REVENUE EVENTS] status:")
    if youtube_db.exists():
        conn = sqlite3.connect(str(youtube_db))
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM revenue_events WHERE kind != 'simulated'")
            count = cursor.fetchone()[0]
            print(f"   - Real/Cooperation Events: {count}")
            
            cursor.execute("SELECT occurred_at, source, amount, kind FROM revenue_events WHERE kind != 'simulated' ORDER BY occurred_at DESC LIMIT 5")
            print("\n   [Latest Real Events]:")
            for row in cursor.fetchall():
                print(f"     - {row[0]} | {row[1]} | ${row[2]:.2f} | [{row[3]}]")
        except Exception as e:
            print(f"   - Error scanning youtube_ai.db: {e}")
        finally:
            conn.close()
    else:
        print("   - youtube_ai.db not found.")

if __name__ == "__main__":
    monitor()
