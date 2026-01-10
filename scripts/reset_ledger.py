#!/usr/bin/env python3
"""
Reset Growth Ledger - Remove all simulated data and prepare for real revenue tracking.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.growth_engine_v1.app import SessionLocal
from modules.growth_engine_v1.models import GrowthLedgerEntry

def backup_ledger():
    """Create a backup of the current ledger before reset."""
    db = SessionLocal()
    try:
        entries = db.query(GrowthLedgerEntry).all()
        backup_file = f"growth_ledger_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(backup_file, 'w') as f:
            f.write(f"Growth Ledger Backup - {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            total_cents = 0
            for entry in entries:
                f.write(f"ID: {entry.id}\n")
                f.write(f"Transaction ID: {entry.transaction_id}\n")
                f.write(f"Stream: {entry.stream}\n")
                f.write(f"Amount: ${entry.amount_cents / 100:.2f} {entry.currency}\n")
                f.write(f"Status: {entry.status}\n")
                f.write(f"Created: {entry.created_at}\n")
                f.write(f"Provenance: {entry.provenance_meta}\n")
                f.write("-" * 80 + "\n")
                total_cents += entry.amount_cents
            
            f.write(f"\nTotal Balance: ${total_cents / 100:.2f}\n")
        
        print(f"✅ Backup created: {backup_file}")
        print(f"📊 Total entries backed up: {len(entries)}")
        print(f"💰 Total balance backed up: ${total_cents / 100:.2f}")
        
        return backup_file
    finally:
        db.close()

def reset_ledger():
    """Delete all entries from the Growth Ledger."""
    db = SessionLocal()
    try:
        count = db.query(GrowthLedgerEntry).count()
        if count == 0:
            print("ℹ️  Ledger is already empty. Nothing to reset.")
            return
        
        print(f"🗑️  Deleting {count} entries from Growth Ledger...")
        db.query(GrowthLedgerEntry).delete()
        db.commit()
        
        print("✅ Growth Ledger reset complete!")
        print("💡 The ledger is now ready for real revenue tracking.")
        
    finally:
        db.close()

def main():
    print("=" * 80)
    print("Growth Ledger Reset Tool")
    print("=" * 80)
    print()
    
    # Step 1: Backup
    print("Step 1: Creating backup...")
    backup_file = backup_ledger()
    print()
    
    # Step 2: Confirm reset
    print("Step 2: Confirm reset")
    print("⚠️  WARNING: This will delete all entries from the Growth Ledger.")
    print(f"📁 Backup saved to: {backup_file}")
    
    response = input("\nProceed with reset? (yes/no): ").strip().lower()
    if response != "yes":
        print("❌ Reset cancelled.")
        return
    
    print()
    
    # Step 3: Reset
    print("Step 3: Resetting ledger...")
    reset_ledger()
    print()
    
    print("=" * 80)
    print("✅ Reset Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Configure live API credentials (SHOPIER_PERSONAL_ACCESS_TOKEN, etc.)")
    print("2. Deploy updated code to Cloud Run")
    print("3. Run first_sale_sprint.py to generate real revenue")
    print()

if __name__ == "__main__":
    main()
