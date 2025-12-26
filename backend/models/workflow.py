from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base

class WorkflowColumn(Base):
    """Model for a Kanban column (e.g., 'Idea', 'Scripting', 'Producing')."""
    __tablename__ = "workflow_columns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    
    # Relationship to cards
    cards = relationship("WorkflowCard", back_populates="column", order_by="WorkflowCard.order")

class WorkflowCard(Base):
    """Model for a card within a workflow column, linked to content/video."""
    __tablename__ = "workflow_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    column_id = Column(Integer, ForeignKey("workflow_columns.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    order = Column(Integer, default=0)
    
    # Optional links
    video_id = Column(String, ForeignKey("video_analytics.video_id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to column
    column = relationship("WorkflowColumn", back_populates="cards")
