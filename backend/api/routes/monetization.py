"""
Monetization API Routes
Revenue tracking and optimization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from backend.core.database import get_db, Video
from backend.core.schemas import SuccessResponse

router = APIRouter()

@router.get("/monetization/overview")
async def get_monetization_overview(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive monetization overview."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get revenue statistics
        revenue_stats = await db.execute(
            select(
                func.sum(Video.revenue).label('total_revenue'),
                func.avg(Video.revenue).label('avg_revenue'),
                func.count(Video.id).label('total_videos'),
                func.sum(Video.views).label('total_views')
            ).where(Video.created_at >= start_date)
        )
        stats = revenue_stats.first()
        
        # Calculate key metrics
        total_revenue = float(stats.total_revenue or 0)
        total_views = stats.total_views or 0
        total_videos = stats.total_videos or 0
        
        rpm = (total_revenue / total_views * 1000) if total_views > 0 else 0  # Revenue per mille
        avg_revenue_per_video = total_revenue / total_videos if total_videos > 0 else 0
        
        # Get top earning videos
        top_earners = await db.execute(
            select(Video)
            .where(Video.created_at >= start_date)
            .order_by(Video.revenue.desc())
            .limit(5)
        )
        
        # Get revenue by category
        category_revenue = await db.execute(
            select(
                Video.category,
                func.sum(Video.revenue).label('revenue'),
                func.count(Video.id).label('video_count')
            )
            .where(Video.created_at >= start_date)
            .group_by(Video.category)
            .order_by(func.sum(Video.revenue).desc())
        )
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "key_metrics": {
                "total_revenue": round(total_revenue, 2),
                "total_views": total_views,
                "total_videos": total_videos,
                "rpm": round(rpm, 2),  # Revenue per 1000 views
                "avg_revenue_per_video": round(avg_revenue_per_video, 2),
                "estimated_monthly_revenue": round(total_revenue * (30 / days), 2)
            },
            "top_earning_videos": [
                {
                    "id": video.id,
                    "title": video.title,
                    "revenue": video.revenue,
                    "views": video.views,
                    "rpm": round((video.revenue / video.views * 1000), 2) if video.views > 0 else 0
                }
                for video in top_earners.scalars().all()
            ],
            "revenue_by_category": [
                {
                    "category": row.category,
                    "revenue": float(row.revenue),
                    "video_count": row.video_count,
                    "avg_revenue_per_video": round(float(row.revenue) / row.video_count, 2)
                }
                for row in category_revenue
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch monetization overview: {str(e)}")

@router.get("/monetization/projections")
async def get_revenue_projections(
    db: AsyncSession = Depends(get_db)
):
    """Get revenue projections based on historical data."""
    try:
        # Get last 90 days of data for projection
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        # Get historical performance
        historical_data = await db.execute(
            select(
                func.date(Video.created_at).label('date'),
                func.sum(Video.revenue).label('daily_revenue'),
                func.sum(Video.views).label('daily_views'),
                func.count(Video.id).label('daily_videos')
            )
            .where(Video.created_at >= start_date)
            .group_by(func.date(Video.created_at))
            .order_by(func.date(Video.created_at))
        )
        
        daily_data = list(historical_data)
        
        if not daily_data:
            return {"message": "Insufficient data for projections"}
        
        # Calculate averages
        total_days = len(daily_data)
        avg_daily_revenue = sum(float(row.daily_revenue) for row in daily_data) / total_days
        avg_daily_views = sum(row.daily_views for row in daily_data) / total_days
        avg_daily_videos = sum(row.daily_videos for row in daily_data) / total_days
        
        # Calculate growth rate (simple linear trend)
        if total_days >= 30:
            recent_avg = sum(float(row.daily_revenue) for row in daily_data[-30:]) / 30
            older_avg = sum(float(row.daily_revenue) for row in daily_data[:30]) / 30
            growth_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            growth_rate = 0
        
        # Generate projections
        projections = {
            "next_7_days": round(avg_daily_revenue * 7 * (1 + growth_rate), 2),
            "next_30_days": round(avg_daily_revenue * 30 * (1 + growth_rate), 2),
            "next_90_days": round(avg_daily_revenue * 90 * (1 + growth_rate), 2),
            "next_365_days": round(avg_daily_revenue * 365 * (1 + growth_rate), 2)
        }
        
        return {
            "historical_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_analyzed": total_days
            },
            "current_performance": {
                "avg_daily_revenue": round(avg_daily_revenue, 2),
                "avg_daily_views": round(avg_daily_views, 0),
                "avg_daily_videos": round(avg_daily_videos, 1),
                "growth_rate": round(growth_rate * 100, 2)  # As percentage
            },
            "revenue_projections": projections,
            "confidence_level": "medium" if total_days >= 30 else "low"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate projections: {str(e)}")

@router.post("/monetization/optimize")
async def get_optimization_suggestions(
    db: AsyncSession = Depends(get_db)
):
    """Get monetization optimization suggestions."""
    try:
        # Analyze top performing content
        top_performers = await db.execute(
            select(Video)
            .where(Video.revenue > 0)
            .order_by((Video.revenue / Video.views).desc())
            .limit(10)
        )
        
        best_videos = list(top_performers.scalars().all())
        
        if not best_videos:
            return {"message": "Insufficient revenue data for optimization suggestions"}
        
        # Analyze patterns in top performers
        category_performance = {}
        duration_performance = {}
        
        for video in best_videos:
            # Category analysis
            if video.category not in category_performance:
                category_performance[video.category] = {
                    "count": 0,
                    "total_rpm": 0,
                    "total_revenue": 0
                }
            
            rpm = (video.revenue / video.views * 1000) if video.views > 0 else 0
            category_performance[video.category]["count"] += 1
            category_performance[video.category]["total_rpm"] += rpm
            category_performance[video.category]["total_revenue"] += video.revenue
            
            # Duration analysis
            duration_bucket = "short" if video.duration < 300 else "medium" if video.duration < 600 else "long"
            if duration_bucket not in duration_performance:
                duration_performance[duration_bucket] = {
                    "count": 0,
                    "total_rpm": 0,
                    "avg_duration": 0
                }
            
            duration_performance[duration_bucket]["count"] += 1
            duration_performance[duration_bucket]["total_rpm"] += rpm
            duration_performance[duration_bucket]["avg_duration"] += video.duration
        
        # Generate suggestions
        suggestions = []
        
        # Best performing categories
        best_category = max(category_performance.items(), 
                          key=lambda x: x[1]["total_rpm"] / x[1]["count"])
        suggestions.append({
            "type": "content_focus",
            "suggestion": f"Focus more on '{best_category[0]}' content",
            "reason": f"Highest RPM: ${round(best_category[1]['total_rpm'] / best_category[1]['count'], 2)} per 1000 views",
            "priority": "high"
        })
        
        # Optimal duration
        best_duration = max(duration_performance.items(),
                          key=lambda x: x[1]["total_rpm"] / x[1]["count"])
        avg_duration = best_duration[1]["avg_duration"] / best_duration[1]["count"]
        suggestions.append({
            "type": "duration_optimization",
            "suggestion": f"Target {best_duration[0]} videos (~{int(avg_duration/60)} minutes)",
            "reason": f"Best performing duration range with highest engagement",
            "priority": "medium"
        })
        
        # Upload frequency
        recent_videos = await db.execute(
            select(func.count(Video.id))
            .where(Video.created_at >= datetime.utcnow() - timedelta(days=30))
        )
        monthly_uploads = recent_videos.scalar()
        
        if monthly_uploads < 8:  # Less than 2 per week
            suggestions.append({
                "type": "upload_frequency",
                "suggestion": "Increase upload frequency to 2-3 videos per week",
                "reason": "Consistent uploads improve algorithm visibility and revenue",
                "priority": "high"
            })
        
        return {
            "analysis_period": "last_90_days",
            "videos_analyzed": len(best_videos),
            "optimization_suggestions": suggestions,
            "performance_insights": {
                "best_performing_category": {
                    "category": best_category[0],
                    "avg_rpm": round(best_category[1]["total_rpm"] / best_category[1]["count"], 2)
                },
                "optimal_duration": {
                    "range": best_duration[0],
                    "avg_minutes": round(avg_duration / 60, 1)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate optimization suggestions: {str(e)}")

@router.put("/videos/{video_id}/revenue")
async def update_video_revenue(
    video_id: str,
    revenue_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Update revenue data for a specific video."""
    try:
        # Get video
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Update revenue
        if "revenue" in revenue_data:
            video.revenue = float(revenue_data["revenue"])
        
        # Update view count if provided
        if "views" in revenue_data:
            video.views = int(revenue_data["views"])
        
        # Update engagement metrics if provided
        if "likes" in revenue_data:
            video.likes = int(revenue_data["likes"])
        
        if "comments" in revenue_data:
            video.comments = int(revenue_data["comments"])
        
        video.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return SuccessResponse(
            message="Video revenue updated successfully",
            data={
                "video_id": video_id,
                "revenue": video.revenue,
                "views": video.views,
                "rpm": round((video.revenue / video.views * 1000), 2) if video.views > 0 else 0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update video revenue: {str(e)}")