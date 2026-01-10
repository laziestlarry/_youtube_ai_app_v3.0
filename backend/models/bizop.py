from sqlalchemy import Column, DateTime, String, Text, JSON
from sqlalchemy.sql import func

from backend.core.database import Base


class BizOpportunity(Base):
    __tablename__ = "biz_opportunities"

    id = Column(String, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    source_id = Column(String, index=True, nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text)
    rationale = Column(Text)
    potential = Column(Text)
    risk = Column(Text)
    quick_return = Column(String)
    priority = Column(String)
    image_url = Column(Text)

    tags = Column(JSON, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
