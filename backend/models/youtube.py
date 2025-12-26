from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base

class ChannelStats(Base):
    """Model for storing YouTube channel statistics."""
    __tablename__ = "channel_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscribers = Column(Integer, default=0)
    views = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", backref="channel_stats")

class VideoAnalytics(Base):
    """Model for storing video-level analytics."""
    __tablename__ = "video_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    channel_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    upload_date = Column(DateTime(timezone=True))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", backref="video_analytics")
