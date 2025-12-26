"""
Monitoring API Routes
Health checks, metrics, and system status
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from backend.core.database import get_db, Video
from backend.utils.monitoring import system_monitor

router = APIRouter()

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check with system metrics."""
    
    # Get system metrics
    system_metrics = system_monitor.get_system_metrics()
    
    # Get database health
    db_health = await system_monitor.get_database_health()
    
    # Get application metrics
    app_metrics = system_monitor.get_application_metrics()
    
    # Get recent activity
    try:
        recent_videos = await db.execute(
            select(func.count(Video.id))
            .where(Video.created_at >= datetime.utcnow() - timedelta(hours=24))
        )
        videos_last_24h = recent_videos.scalar()
    except:
        videos_last_24h = 0
    
    # Determine overall health
    overall_status = "healthy"
    issues = []
    
    if system_metrics.get("cpu_percent", 0) > 90:
        issues.append("High CPU usage")
        overall_status = "degraded"
    
    if system_metrics.get("memory", {}).get("percent", 0) > 90:
        issues.append("High memory usage")
        overall_status = "degraded"
    
    if db_health.get("status") != "healthy":
        issues.append("Database connectivity issues")
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "issues": issues,
        "system": system_metrics,
        "database": db_health,
        "application": app_metrics,
        "activity": {
            "videos_created_last_24h": videos_last_24h
        }
    }

@router.get("/metrics")
async def get_application_metrics(db: AsyncSession = Depends(get_db)):
    """Get application performance metrics."""
    
    try:
        # Get video statistics
        total_videos = await db.execute(select(func.count(Video.id)))
        total_views = await db.execute(select(func.sum(Video.views)))
        total_revenue = await db.execute(select(func.sum(Video.revenue)))
        
        # Get recent activity
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_videos = await db.execute(
            select(func.count(Video.id))
            .where(Video.created_at >= last_24h)
        )
        
        last_7d = datetime.utcnow() - timedelta(days=7)
        weekly_videos = await db.execute(
            select(func.count(Video.id))
            .where(Video.created_at >= last_7d)
        )
        
        return {
            "content_metrics": {
                "total_videos": total_videos.scalar() or 0,
                "total_views": total_views.scalar() or 0,
                "total_revenue": float(total_revenue.scalar() or 0),
                "videos_last_24h": recent_videos.scalar() or 0,
                "videos_last_7d": weekly_videos.scalar() or 0
            },
            "system_metrics": system_monitor.get_system_metrics(),
            "application_metrics": system_monitor.get_application_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Failed to fetch metrics: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/status")
async def get_system_status():
    """Get current system status summary."""
    
    system_metrics = system_monitor.get_system_metrics()
    app_metrics = system_monitor.get_application_metrics()
    
    # Determine status
    status = "operational"
    if system_metrics.get("cpu_percent", 0) > 80:
        status = "degraded"
    if system_metrics.get("memory", {}).get("percent", 0) > 85:
        status = "degraded"
    
    return {
        "status": status,
        "uptime": app_metrics["uptime"],
        "cpu_usage": f"{system_metrics.get('cpu_percent', 0):.1f}%",
        "memory_usage": f"{system_metrics.get('memory', {}).get('percent', 0):.1f}%",
        "disk_usage": f"{system_metrics.get('disk', {}).get('percent', 0):.1f}%",
        "timestamp": datetime.utcnow().isoformat()
    }