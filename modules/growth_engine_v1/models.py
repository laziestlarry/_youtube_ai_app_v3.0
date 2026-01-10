from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, func, ForeignKey
from backend.core.database import Base
from datetime import datetime

class ProvenanceMixin:
    """Standard fields for data lineage."""
    provenance_meta = Column(JSON, nullable=True, comment="Origin: name, type, license, quality_score")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GrowthLedgerEntry(Base, ProvenanceMixin):
    """The heavy duty financial truth."""
    __tablename__ = "growth_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    stream = Column(String, index=True)  # POD, AFFILIATE, CONTENT
    amount_cents = Column(Integer, nullable=False) # Store in cents
    currency = Column(String, default="USD")
    status = Column(String, default="PENDING") # PENDING, CLEARED, DISPUTED
    payout_id = Column(Integer, ForeignKey("growth_payouts.id"), nullable=True)
    
class GrowthOrder(Base, ProvenanceMixin):
    """Permissive order intake."""
    __tablename__ = "growth_orders"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    source = Column(String, index=True) # shopify, etsy, amazon
    status = Column(String)
    total_price = Column(Float)
    currency = Column(String)
    customer_hash = Column(String, index=True) # PII Hashed
    items_json = Column(JSON) # Flexible storage for line items

class GrowthTraffic(Base, ProvenanceMixin):
    """Aggregated traffic stats."""
    __tablename__ = "growth_traffic"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True)
    source = Column(String)
    medium = Column(String)
    campaign = Column(String)
    sessions = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

class GrowthAdSpend(Base, ProvenanceMixin):
    """Ad spend tracker."""
    __tablename__ = "growth_ad_spend"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True)
    platform = Column(String) # meta, google, tiktok
    campaign_id = Column(String)
    creative_id = Column(String)
    spend_micros = Column(Integer) # Store precise spend
    impressions = Column(Integer)
    clicks = Column(Integer)

class GrowthSku(Base, ProvenanceMixin):
    """Product Catalog."""
    __tablename__ = "growth_skus"
    
    id = Column(Integer, primary_key=True, index=True)
    sku_code = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String) # Tee, Mug, Poster, Case
    tags = Column(String) # JSON or comma-separated
    cost_basis_cents = Column(Integer)
    price_cents = Column(Integer)
    status = Column(String, default="active")

class BusinessMission(Base, ProvenanceMixin):
    """Core Business Mission & Vision."""
    __tablename__ = "business_missions"

    id = Column(Integer, primary_key=True, index=True)
    vision = Column(Text, nullable=False)
    values = Column(JSON)
    north_star_metric = Column(String, default="daily_net_revenue")

class BusinessWorkflow(Base, ProvenanceMixin):
    """Operational Workflows logic."""
    __tablename__ = "business_workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    trigger_event = Column(String) # e.g., 'payment_completed'
    logic_steps = Column(JSON)  # Array of ordered steps/actions
    is_autonomous = Column(Integer, default=1) # Boolean 1/0 for SQL compatibility

class AIProtocol(Base, ProvenanceMixin):
    """AI Execution Protocols & Fine-tuning parameters."""
    __tablename__ = "ai_protocols"

    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String, index=True) # e.g., 'fulfillment_engine'
    prompt_template = Column(Text)
    model_params = Column(JSON)
    validation_regex = Column(String)

class GrowthPayout(Base, ProvenanceMixin):
    """Orchestrated bank settlements."""
    __tablename__ = "growth_payouts"

    id = Column(Integer, primary_key=True, index=True)
    payout_id = Column(String, unique=True, index=True) # e.g. TR-12345
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    destination_bank = Column(String)
    status = Column(String, default="INITIATED") # INITIATED, PROCESSING, COMPLETED, FAILED
    ledger_count = Column(Integer) # Number of ledger entries settled in this payout

