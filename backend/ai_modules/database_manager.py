import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
import structlog

logger = structlog.get_logger()

Base = declarative_base()

class VideoRecord(Base):
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    youtube_id = Column(String(20), unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(JSON)
    category = Column(String(100))
    duration = Column(Integer)  # seconds
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    record_metadata = Column(JSON)

class MonetizationRecord(Base):
    __tablename__ = "monetization"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), nullable=False)
    ad_revenue = Column(Float, default=0.0)
    sponsorship_revenue = Column(Float, default=0.0)
    affiliate_revenue = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)
    rpm = Column(Float, default=0.0)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsRecord(Base):
    __tablename__ = "analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    record_metadata = Column(JSON)

class ContentIdea(Base):
    __tablename__ = "content_ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    keywords = Column(JSON)
    estimated_views = Column(Integer)
    estimated_revenue = Column(Float)
    priority_score = Column(Float, default=0.0)
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_for = Column(DateTime)

class DatabaseManager:
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = None
        self.session_factory = None
        
    def _get_database_url(self) -> str:
        """Get database URL from environment."""
        import os
        return os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:password@localhost:5432/youtube_ai"
        )
    
    async def initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.session_factory() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    async def save_video_record(self, video_data: Dict[str, Any]) -> str:
        """Save video record to database."""
        try:
            async with self.session_factory() as session:
                video = VideoRecord(
                    youtube_id=video_data.get("youtube_id"),
                    title=video_data.get("title"),
                    description=video_data.get("description"),
                    tags=video_data.get("tags", []),
                    category=video_data.get("category"),
                    duration=video_data.get("duration"),
                    views=video_data.get("views", 0),
                    likes=video_data.get("likes", 0),
                    comments=video_data.get("comments", 0),
                    shares=video_data.get("shares", 0),
                    engagement_rate=video_data.get("engagement_rate", 0.0),
                    published_at=video_data.get("published_at"),
                    record_metadata=video_data.get("metadata", {})
                )
                
                session.add(video)
                await session.commit()
                await session.refresh(video)
                
                logger.info("Video record saved", video_id=str(video.id))
                return str(video.id)
                
        except Exception as e:
            logger.error("Failed to save video record", error=str(e))
            raise
    
    async def save_monetization_record(self, monetization_data: Dict[str, Any]) -> str:
        """Save monetization record to database."""
        try:
            async with self.session_factory() as session:
                monetization = MonetizationRecord(
                    video_id=monetization_data.get("video_id"),
                    ad_revenue=monetization_data.get("ad_revenue", 0.0),
                    sponsorship_revenue=monetization_data.get("sponsorship_revenue", 0.0),
                    affiliate_revenue=monetization_data.get("affiliate_revenue", 0.0),
                    total_revenue=monetization_data.get("total_revenue", 0.0),
                    cpm=monetization_data.get("cpm", 0.0),
                    rpm=monetization_data.get("rpm", 0.0),
                    date=monetization_data.get("date", datetime.utcnow())
                )
                
                session.add(monetization)
                await session.commit()
                await session.refresh(monetization)
                
                logger.info("Monetization record saved", record_id=str(monetization.id))
                return str(monetization.id)
                
        except Exception as e:
            logger.error("Failed to save monetization record", error=str(e))
            raise
    
    async def get_video_analytics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get video analytics for the specified period."""
        try:
            async with self.session_factory() as session:
                from sqlalchemy import select
                
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                stmt = select(VideoRecord).where(
                    VideoRecord.created_at >= cutoff_date
                ).order_by(VideoRecord.created_at.desc())
                
                result = await session.execute(stmt)
                videos = result.scalars().all()
                
                return [
                    {
                        "id": str(video.id),
                        "youtube_id": video.youtube_id,
                        "title": video.title,
                        "views": video.views,
                        "likes": video.likes,
                        "comments": video.comments,
                        "engagement_rate": video.engagement_rate,
                        "published_at": video.published_at.isoformat() if video.published_at else None,
                        "category": video.category
                    }
                    for video in videos
                ]
                
        except Exception as e:
            logger.error("Failed to get video analytics", error=str(e))
            raise
    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")