from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.core.database import Base

class ContentIdea(Base):
    """Model for a content idea before it becomes a video."""
    __tablename__ = "content_ideas"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    priority = Column(Integer, default=1)  # 1-3
    status = Column(String, default="pending")  # pending, generated, in_progress, completed
    generated_content = Column(JSON, nullable=True)  # Store AI output
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
