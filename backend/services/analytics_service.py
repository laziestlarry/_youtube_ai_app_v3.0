from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from backend.models.youtube import ChannelStats, VideoAnalytics
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.cache = {}
    
    async def get_channel_stats(self, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Get real channel statistics from DB."""
        try:
            result = await db.execute(
                select(ChannelStats)
                .where(ChannelStats.user_id == user_id)
                .order_by(ChannelStats.fetched_at.desc())
            )
            stats = result.scalars().first()
            
            if not stats:
                return {
                    "subscriber_count": 0,
                    "view_count": 0,
                    "video_count": 0,
                    "estimated_revenue": 0.0
                }
            
            return {
                "subscriber_count": stats.subscribers,
                "view_count": stats.views,
                "video_count": stats.video_count,
                "estimated_revenue": stats.revenue
            }
        except Exception as e:
            logger.error(f"Error in get_channel_stats: {str(e)}", exc_info=True)
            raise e
    
    async def get_views_history(self, user_id: int, days: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get historical view data points."""
        try:
            result = await db.execute(
                select(
                    func.date(VideoAnalytics.upload_date).label('date'),
                    func.sum(VideoAnalytics.views).label('total_views')
                )
                .where(
                    VideoAnalytics.user_id == user_id,
                    VideoAnalytics.upload_date >= datetime.now() - timedelta(days=days)
                )
                .group_by(func.date(VideoAnalytics.upload_date))
                .order_by(func.date(VideoAnalytics.upload_date))
            )
            rows = result.all()
            return [{"date": str(row.date), "views": row.total_views or 0} for row in rows]
        except Exception as e:
            logger.error(f"Error in get_views_history: {str(e)}", exc_info=True)
            return []

    async def get_revenue_history(self, user_id: int, days: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get historical revenue data points."""
        # Simplified: generate data based on video analytic fetched dates or channel stat snapshots
        # In a real app we'd have a 'DailyStats' table. Here we group VideoAnalytics by upload date.
        try:
            result = await db.execute(
                select(
                    func.date(VideoAnalytics.upload_date).label('date'),
                    func.sum(VideoAnalytics.revenue).label('total_revenue')
                )
                .where(
                    VideoAnalytics.user_id == user_id,
                    VideoAnalytics.upload_date >= datetime.now() - timedelta(days=days)
                )
                .group_by(func.date(VideoAnalytics.upload_date))
                .order_by(func.date(VideoAnalytics.upload_date))
            )
            rows = result.all()
            return [{"date": str(row.date), "revenue": row.total_revenue or 0.0} for row in rows]
        except Exception as e:
            logger.error(f"Error in get_revenue_history: {str(e)}", exc_info=True)
            return []

    async def forecast_revenue(self, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Project revenue for the next 30 days based on last 30 days growth."""
        try:
            history = await self.get_revenue_history(user_id, 30, db)
            if not history or len(history) < 2:
                return {"projected_revenue": 0.0, "confidence": "low"}
            
            total_past = sum(d["revenue"] for d in history)
            # Simple average growth project
            daily_avg = total_past / len(history)
            projected = daily_avg * 30 * 1.05  # Assume 5% growth
            
            return {
                "projected_revenue": round(projected, 2),
                "confidence": "medium",
                "basis": "30-day moving average + 5% growth"
            }
        except Exception as e:
            logger.error(f"Error in forecast_revenue: {str(e)}", exc_info=True)
            return {"projected_revenue": 0.0, "error": str(e)}

    async def get_recent_videos(self, user_id: int, limit: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get recent video analytics."""
        try:
            result = await db.execute(
                select(VideoAnalytics)
                .where(VideoAnalytics.user_id == user_id)
                .order_by(VideoAnalytics.upload_date.desc())
                .limit(limit)
            )
            videos = result.scalars().all()
            return [
                {
                    "video_id": v.video_id,
                    "title": v.title,
                    "views": v.views,
                    "likes": v.likes,
                    "comments": v.comments,
                    "revenue": v.revenue,
                    "upload_date": v.upload_date.isoformat() if v.upload_date else None
                }
                for v in videos
            ]
        except Exception as e:
            logger.error(f"Error in get_recent_videos: {str(e)}", exc_info=True)
            return []

analytics_service = AnalyticsService()