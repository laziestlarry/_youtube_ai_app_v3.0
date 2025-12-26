from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from datetime import datetime, timedelta

from backend.core.database import get_async_db as get_db
from backend.api.deps import get_current_user
from backend.models.user import User
from backend.services.analytics_service import analytics_service

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics summary for the current user."""
    try:
        stats = await analytics_service.get_channel_stats(current_user.id, db)
        forecast = await analytics_service.forecast_revenue(current_user.id, db)
        recent_videos = await analytics_service.get_recent_videos(current_user.id, 10, db)
        
        return {
            "stats": stats,
            "forecast": forecast,
            "recent_videos": recent_videos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue-history")
async def get_revenue_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical revenue data."""
    try:
        history = await analytics_service.get_revenue_history(current_user.id, days, db)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-metrics")
async def get_performance_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed performance metrics for charts."""
    try:
        views = await analytics_service.get_views_history(current_user.id, days, db)
        revenue = await analytics_service.get_revenue_history(current_user.id, days, db)
        
        return {
            "views": views,
            "revenue": revenue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))