from sqlalchemy.orm import Session
from .models import GrowthLedgerEntry
from typing import Dict, Any

class MonetizationService:
    """
    Handles ingestion of non-order revenue:
    - Content (AdSense, YouTube Revenue)
    - Affiliate (Amazon Associates, ClickBank)
    """
    
    def __init__(self, db: Session):
        self.db = db

    def ingest_payout(self, source: str, payload: Dict[str, Any], provenance: Dict[str, Any]):
        """
        Ingest a payout event.
        Payload expectations depend on source, but generally:
        { "amount": 123.45, "currency": "USD", "date": "...", "ref_id": "..." }
        """
        
        # Normalize
        amount = float(payload.get("amount", 0))
        currency = payload.get("currency", "USD")
        ref_id = payload.get("ref_id") or payload.get("transaction_id") or f"payout_{source}_{payload.get('date', 'unknown')}"
        
        # Determine Stream
        stream = "CONTENT" # Default
        if "affiliate" in source.lower() or "amazon" in source.lower():
            stream = "AFFILIATE"
        elif "adsense" in source.lower() or "youtube" in source.lower():
            stream = "CONTENT"
            
        # Check Idempotency
        existing = self.db.query(GrowthLedgerEntry).filter_by(transaction_id=str(ref_id)).first()
        if existing:
            return {"status": "skipped", "reason": "duplicate"}
            
        # Create Ledger Entry
        entry = GrowthLedgerEntry(
            transaction_id=str(ref_id),
            stream=stream,
            amount_cents=int(amount * 100),
            currency=currency,
            status="CLEARED", # Payouts are usually cleared upon receipt
            provenance_meta=provenance
        )
        
        self.db.add(entry)
        self.db.commit()
        
        return {"status": "ingested", "id": entry.id, "stream": stream, "amount": amount}

    def ingest_batch_payout(self, source: str, items: list, provenance: Dict[str, Any]):
        results = []
        for item in items:
            results.append(self.ingest_payout(source, item, provenance))
        return {"processed": len(results), "details": results}

