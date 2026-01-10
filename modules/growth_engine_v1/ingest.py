from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import json
from .models import GrowthOrder, GrowthLedgerEntry, GrowthTraffic, GrowthAdSpend

class IngestionService:
    def __init__(self, db: Session):
        self.db = db

    def hash_pii(self, raw_str: str) -> str:
        """Simple SHA256 hash for privacy."""
        if not raw_str: return None
        return hashlib.sha256(raw_str.encode()).hexdigest()

    def ingest_order(self, data: dict, provenance: dict):
        """Ingest an order permissively."""
        # Check if exists
        existing = self.db.query(GrowthOrder).filter_by(external_id=str(data.get("id"))).first()
        if existing:
            # Idempotency: Update or Skip
            return {"status": "skipped", "reason": "duplicate"}

        # Hash PII
        customer_email = data.get("email") or data.get("customer", {}).get("email")
        
        order = GrowthOrder(
            external_id=str(data.get("id")),
            source=provenance.get("origin_name", "unknown"),
            status=data.get("status", "unknown"),
            total_price=float(data.get("total_price", 0)),
            currency=data.get("currency", "USD"),
            customer_hash=self.hash_pii(customer_email),
            items_json=data.get("line_items", []),
            provenance_meta=provenance
        )
        self.db.add(order)
        
        # Auto-create Ledger Entry if paid
        if order.status in ["paid", "fulfilled", "complete"]:
             ledger = GrowthLedgerEntry(
                 transaction_id=f"order_{order.external_id}",
                 stream="POD",  # Defaulting to POD for now, logic can be smarter
                 amount_cents=int(order.total_price * 100),
                 status="CLEARED",
                 provenance_meta=provenance
             )
             self.db.add(ledger)
             
        self.db.commit()
        return {"status": "ingested", "id": order.id}

    def ingest_generic(self, topic: str, data: dict, provenance: dict):
        """Generic intake router."""
        if topic == "orders":
            return self.ingest_order(data, provenance)
        # Add other topics here
        return {"status": "ignored", "reason": f"unknown topic {topic}"}
