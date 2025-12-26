"""
Admin API Routes
Administrative functions, backups, and system management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Dict, Any

from backend.core.database import get_db, Video, ContentIdea
from backend.services.backup_service import backup_service
from backend.utils.monitoring import system_monitor

router = APIRouter()

@router.post("/admin/backup/create")
async def create_backup(background_tasks: BackgroundTasks):
    """Create a full system backup."""
    try:
        # Run backup in background
        background_tasks.add_task(backup_service.create_full_backup)
        
        return {
            "status": "success",
            "message": "Backup process started",
            "note": "Backup will be created in the background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start backup: {str(e)}")

@router.get("/admin/backup/list")
async def list_backups():
    """List all available backups."""
    try:
        backups = backup_service.list_backups()
        return {
            "status": "success",
            "backups": backups,
            "total_backups": len(backups)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@router.post("/admin/backup/cleanup")
async def cleanup_backups(keep_days: int = 30):
    """Clean up old backups."""
    try:
        result = backup_service.cleanup_old_backups(keep_days)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup backups: {str(e)}")

@router.get("/admin/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """Get comprehensive admin statistics."""
    try:
        # Database statistics
        total_videos = await db.execute(select(func.count(Video.id)))
        total_ideas = await db.execute(select(func.count(ContentIdea.id)))
        total_views = await db.execute(select(func.sum(Video.views)))
        total_revenue = await db.execute(select(func.sum(Video.revenue)))
        
        # System metrics
        system_metrics = system_monitor.get_system_metrics()
        app_metrics = system_monitor.get_application_metrics()
        
        # Recent activity
        from datetime import datetime, timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_videos = await db.execute(
            select(func.count(Video.id))
            .where(Video.created_at >= last_24h)
        )
        
        return {
            "database_stats": {
                "total_videos": total_videos.scalar() or 0,
                "total_content_ideas": total_ideas.scalar() or 0,
                "total_views": total_views.scalar() or 0,
                "total_revenue": float(total_revenue.scalar() or 0),
                "videos_last_24h": recent_videos.scalar() or 0
            },
            "system_stats": {
                "cpu_usage": system_metrics.get("cpu_percent", 0),
                "memory_usage": system_metrics.get("memory", {}).get("percent", 0),
                "disk_usage": system_metrics.get("disk", {}).get("percent", 0),
                "uptime": app_metrics["uptime"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get admin stats: {str(e)}")

@router.post("/admin/maintenance/cleanup")
async def run_maintenance_cleanup(db: AsyncSession = Depends(get_db)):
    """Run maintenance cleanup tasks."""
    try:
        cleanup_results = {}
        
        # Clean up old temporary files
        import os
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_files_removed = 0
        
        try:
            for file in os.listdir(temp_dir):
                if file.startswith("youtube_ai_"):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        # Remove files older than 1 day
                        if os.path.getmtime(file_path) < (datetime.utcnow().timestamp() - 86400):
                            os.remove(file_path)
                            temp_files_removed += 1
        except:
            pass
        
        cleanup_results["temp_files_removed"] = temp_files_removed
        
        # Clean up old backup files
        backup_cleanup = backup_service.cleanup_old_backups(30)
        cleanup_results["old_backups_removed"] = backup_cleanup.get("removed_count", 0)
        
        return {
            "status": "success",
            "message": "Maintenance cleanup completed",
            "results": cleanup_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Maintenance cleanup failed: {str(e)}")

@router.get("/admin/logs")
async def get_recent_logs(lines: int = 100):
    """Get recent application logs."""
    try:
        import os
        log_file = "logs/app.log"
        
        if not os.path.exists(log_file):
            return {"message": "Log file not found"}
        
        # Read last N lines
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "status": "success",
            "lines_requested": lines,
            "lines_returned": len(recent_lines),
            "logs": [line.strip() for line in recent_lines]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@router.post("/admin/reset/demo")
async def reset_demo_data(db: AsyncSession = Depends(get_db)):
    """Reset database with demo data (development only)."""
    try:
        from backend.core.config import settings
        
        if settings.ENVIRONMENT == "production":
            raise HTTPException(status_code=403, detail="Demo reset not allowed in production")
        
        # Clear existing data
        await db.execute(delete(Video))
        await db.execute(delete(ContentIdea))
        await db.commit()
        
        # Create demo content ideas
        demo_ideas = [
            {
                "title": "AI Tools for Content Creators",
                "description": "Review of the best AI tools for YouTube creators",
                "category": "technology",
                "priority": 9
            },
            {
                "title": "Monetization Strategies 2024",
                "description": "Latest strategies for YouTube monetization",
                "category": "business",
                "priority": 8
            },
            {
                "title": "Content Creation Workflow",
                "description": "My complete content creation process",
                "category": "tutorial",
                "priority": 7
            }
        ]
        
        for idea_data in demo_ideas:
            idea = ContentIdea(**idea_data)
            db.add(idea)
        
        await db.commit()
        
        return {
            "status": "success",
            "message": "Demo data reset completed",
            "demo_ideas_created": len(demo_ideas)
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reset demo data: {str(e)}")