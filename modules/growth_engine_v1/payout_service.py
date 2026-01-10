from sqlalchemy.orm import Session
from .models import GrowthLedgerEntry, GrowthPayout
from typing import Dict, Any, List
import uuid

class PayoutService:
    def __init__(self, db: Session):
        self.db = db

    def orchestrate_payout(self, destination_bank: str = "AutonomaX Global Reserve") -> Dict[str, Any]:
        """
        Sweeps all CLEARED entries that haven't been paid out yet.
        """
        # 1. Fetch Cleared but Unpaid Entries
        unpaid_entries = self.db.query(GrowthLedgerEntry).filter(
            GrowthLedgerEntry.status == "CLEARED",
            GrowthLedgerEntry.payout_id == None
        ).all()
        
        if not unpaid_entries:
            return {"status": "skipped", "reason": "no_cleared_funds"}
            
        total_cents = sum(e.amount_cents for e in unpaid_entries)
        
        # 2. Create Payout Instruction
        payout_ref = f"TR-{uuid.uuid4().hex[:8].upper()}"
        payout = GrowthPayout(
            payout_id=payout_ref,
            amount_cents=total_cents,
            destination_bank=destination_bank,
            status="PROCESSING",
            ledger_count=len(unpaid_entries),
            provenance_meta={"origin": "PayoutService", "type": "AutomatedSweep"}
        )
        
        self.db.add(payout)
        self.db.flush() # Get payout.id
        
        # 3. Associate Entries
        for entry in unpaid_entries:
            entry.payout_id = payout.id
            
        self.db.commit()
        
        return {
            "status": "initiated",
            "payout_ref": payout_ref,
            "total_amount": total_cents / 100.0,
            "entry_count": len(unpaid_entries),
            "destination": destination_bank
        }

    def list_payouts(self) -> List[GrowthPayout]:
        return self.db.query(GrowthPayout).all()
