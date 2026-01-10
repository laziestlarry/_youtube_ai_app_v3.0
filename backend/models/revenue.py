from sqlalchemy import Column, DateTime, Float, JSON, String, Text
from sqlalchemy.sql import func

from backend.core.database import Base


class RevenueEvent(Base):
    __tablename__ = "revenue_events"

    id = Column(String, primary_key=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    source = Column(Text, nullable=False)
    kind = Column(String, nullable=False, default="simulated")
    asset_url = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
