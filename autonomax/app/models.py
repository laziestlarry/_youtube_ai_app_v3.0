from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True, index=True)
    title = Column(String(500))
    description = Column(Text)
    status = Column(String(50), default="draft")
    price_usd = Column(Float)
    meta = Column(JSON)
    assets = relationship("Asset", back_populates="product")
    created_at = Column(DateTime, default=datetime.utcnow)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    kind = Column(String(50))  # image, zip, license
    path_or_url = Column(String(1000))
    product = relationship("Product", back_populates="assets")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    payload_json = Column(JSON)
    status = Column(String(50), default=JobStatus.QUEUED.value)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class AutomationBlueprint(Base):
    __tablename__ = "automation_blueprints"
    id = Column(Integer, primary_key=True)
    keyword_niche = Column(String(300), index=True, unique=True)
    est_volume_raw = Column(String(50))
    avg_price_raw = Column(String(50))
    competitors = Column(Text)
    winning_hook = Column(Text)
    est_volume = Column(Integer, default=0)
    avg_price_usd = Column(Float, default=0.0)
    revenue_potential = Column(Float, default=0.0)
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class AffiliateProgram(Base):
    __tablename__ = "affiliate_programs"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, index=True)
    signup_url = Column(String(1000))
    category = Column(String(200))
    commission_raw = Column(String(50))
    commission_rate = Column(Float)
    recurring = Column(String(10), default="No")
    created_at = Column(DateTime, default=datetime.utcnow)

class InfluencerSource(Base):
    __tablename__ = "influencer_sources"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), index=True)
    channel_url = Column(String(1000))
    contact_email = Column(String(200))
    notes = Column(Text)
    status = Column(String(50), default="queued")
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowExtraction(Base):
    __tablename__ = "workflow_extractions"
    id = Column(Integer, primary_key=True)
    source_type = Column(String(50))
    source_ref = Column(String(200))
    steps_json = Column(JSON)
    status = Column(String(50), default="queued")
    created_at = Column(DateTime, default=datetime.utcnow)

class ProtocolBinding(Base):
    __tablename__ = "protocol_bindings"
    id = Column(Integer, primary_key=True)
    target_path = Column(String(1000), index=True)
    protocol_name = Column(String(200))
    files_json = Column(JSON)
    summary = Column(Text)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkItem(Base):
    __tablename__ = "work_items"
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    category = Column(String(100))
    status = Column(String(50), default="scheduled")
    priority_score = Column(Float, default=0.0)
    focus = Column(Integer, default=0)
    due_at = Column(DateTime)
    source_type = Column(String(50))
    source_ref = Column(String(200))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
