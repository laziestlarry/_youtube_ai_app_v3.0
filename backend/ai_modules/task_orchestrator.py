import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from fastapi import APIRouter, HTTPException, BackgroundTasks
import structlog

from .database_manager import DatabaseManager
from .content_generator import ContentGenerator
from .monetization_tracker import MonetizationTracker
from .advanced_analytics import AdvancedAnalyticsEngine
from .upload_manager import UploadManager

logger = structlog.get_logger()

# Celery configuration
celery_app = Celery(
    "youtube_ai_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["ai_modules.task_orchestrator"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "generate_daily_content": {
        "task": "ai_modules.task_orchestrator.generate_daily_content",
        "schedule": crontab(hour=8, minute=0),  # 8 AM daily
    },
    "update_analytics": {
        "task": "ai_modules.task_orchestrator.update_analytics",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "process_monetization": {
        "task": "ai_modules.task_orchestrator.process_monetization",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
    },
    "cleanup_old_files": {
        "task": "ai_modules.task_orchestrator.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
}

class TaskOrchestrator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.content_generator = ContentGenerator()
        self.monetization_tracker = MonetizationTracker()
        self.analytics_engine = AdvancedAnalyticsEngine()
        self.upload_manager = UploadManager()
        
    async def orchestrate_content_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete content generation pipeline."""
        try:
            pipeline_id = f"pipeline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info("Starting content pipeline", pipeline_id=pipeline_id)
            
            # Step 1: Generate content ideas
            ideas = await self.content_generator.generate_content_ideas(
                category=config.get("category", "ai_monetization"),
                count=config.get("idea_count", 5)
            )
            
            # Step 2: Select best idea based on analytics
            selected_idea = await self.analytics_engine.select_optimal_content_idea(ideas)
            
            # Step 3: Generate script
            script = await self.content_generator.generate_script(
                idea=selected_idea,
                target_duration=config.get("target_duration", 600)  # 10 minutes
            )
            
            # Step 4: Generate video
            video_data = await self.content_generator.generate_video(
                script=script,
                style=config.get("video_style", "professional")
            )
            
            # Step 5: Upload to storage
            upload_result = await self.upload_manager.upload_video(
                video_path=video_data["video_path"],
                metadata=video_data["metadata"]
            )
            
            # Step 6: Schedule for YouTube upload
            schedule_result = await self.schedule_youtube_upload(
                video_data=video_data,
                upload_result=upload_result,
                schedule_time=config.get("schedule_time")
            )
            
            # Step 7: Save to database
            video_id = await self.db_manager.save_video_record({
                "title": video_data["title"],
                "description": video_data["description"],
                "tags": video_data["tags"],
                "category": selected_idea["category"],
                "duration": video_data["duration"],
                "metadata": {
                    "pipeline_id": pipeline_id,
                    "upload_result": upload_result,
                    "schedule_result": schedule_result
                }
            })
            
            result = {
                "pipeline_id": pipeline_id,
                "video_id": video_id,
                "status": "completed",
                "steps_completed": 7,
                "video_data": video_data,
                "upload_result": upload_result,
                "schedule_result": schedule_result
            }
            
            logger.info("Content pipeline completed", pipeline_id=pipeline_id, video_id=video_id)
            return result
            
        except Exception as e:
            logger.error("Content pipeline failed", pipeline_id=pipeline_id, error=str(e))
            raise
    
    async def schedule_youtube_upload(self, video_data: Dict[str, Any], upload_result: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Schedule video for YouTube upload."""
        try:
            if not schedule_time:
                # Schedule for optimal posting time (based on analytics)
                optimal_time = await self.analytics_engine.get_optimal_posting_time()
                schedule_time = optimal_time
            
            # Queue the upload task
            task = upload_to_youtube.apply_async(
                args=[video_data, upload_result],
                eta=schedule_time
            )
            
            return {
                "task_id": task.id,
                "scheduled_for": schedule_time.isoformat(),
                "status": "scheduled"
            }
            
        except Exception as e:
            logger.error("Failed to schedule YouTube upload", error=str(e))
            raise

# Celery Tasks
@celery_app.task(bind=True, max_retries=3)
def generate_daily_content(self):
    """Generate daily content automatically."""
    try:
        logger.info("Starting daily content generation")
        
        orchestrator = TaskOrchestrator()
        
        # Get configuration from database or use defaults
        config = {
            "category": "ai_monetization",
            "idea_count": 3,
            "target_duration": 600,
            "video_style": "professional"
        }
        
        # Run the pipeline
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            orchestrator.orchestrate_content_pipeline(config)
        )
        
        logger.info("Daily content generation completed", result=result)
        return result
        
    except Exception as e:
        logger.error("Daily content generation failed", error=str(e))
        self.retry(countdown=60 * 5)  # Retry in 5 minutes

@celery_app.task(bind=True, max_retries=3)
def update_analytics(self):
    """Update analytics data from YouTube API."""
    try:
        logger.info("Starting analytics update")
        
        db_manager = DatabaseManager()
        analytics_engine = AdvancedAnalyticsEngine()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get recent videos
        videos = loop.run_until_complete(
            db_manager.get_video_analytics(days=7)
        )
        
        # Update analytics for each video
        for video in videos:
            if video.get("youtube_id"):
                analytics_data = loop.run_until_complete(
                    analytics_engine.fetch_youtube_analytics(video["youtube_id"])
                )
                
                # Update database with new analytics
                loop.run_until_complete(
                    db_manager.update_video_analytics(video["id"], analytics_data)
                )
        
        logger.info("Analytics update completed", videos_updated=len(videos))
        return {"videos_updated": len(videos)}
        
    except Exception as e:
        logger.error("Analytics update failed", error=str(e))
        self.retry(countdown=60 * 10)  # Retry in 10 minutes

@celery_app.task(bind=True, max_retries=3)
def process_monetization(self):
    """Process monetization data and update earnings."""
    try:
        logger.info("Starting monetization processing")
        
        monetization_tracker = MonetizationTracker()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Process earnings for recent videos
        result = loop.run_until_complete(
            monetization_tracker.process_recent_earnings()
        )
        
        logger.info("Monetization processing completed", result=result)
        return result
        
    except Exception as e:
        logger.error("Monetization processing failed", error=str(e))
        self.retry(countdown=60 * 15)  # Retry in 15 minutes

@celery_app.task(bind=True, max_retries=3)
def upload_to_youtube(self, video_data: Dict[str, Any], upload_result: Dict[str, Any]):
    """Upload video to YouTube."""
    try:
        logger.info("Starting YouTube upload", video_title=video_data.get("title"))
        
        upload_manager = UploadManager()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Upload to YouTube
        youtube_result = loop.run_until_complete(
            upload_manager.upload_to_youtube(video_data, upload_result)
        )
        
        # Update database with YouTube ID
        if youtube_result.get("youtube_id"):
            db_manager = DatabaseManager()
            loop.run_until_complete(
                db_manager.update_video_youtube_id(
                    video_data["video_id"],
                    youtube_result["youtube_id"]
                )
            )
        
        logger.info("YouTube upload completed", youtube_id=youtube_result.get("youtube_id"))
        return youtube_result
        
    except Exception as e:
        logger.error("YouTube upload failed", error=str(e))
        self.retry(countdown=60 * 30)  # Retry in 30 minutes

@celery_app.task
def cleanup_old_files():
    """Clean up old temporary files."""
    try:
        import os
        import shutil
        from pathlib import Path
        
        logger.info("Starting file cleanup")
        
        temp_dirs = ["/app/temp", "/app/uploads/temp"]
        cutoff_time = datetime.now() - timedelta(days=7)
        
        files_deleted = 0
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for file_path in Path(temp_dir).rglob("*"):
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            try:
                                file_path.unlink()
                                files_deleted += 1
                            except Exception as e:
                                logger.warning("Failed to delete file", file=str(file_path), error=str(e))
        
        logger.info("File cleanup completed", files_deleted=files_deleted)
        return {"files_deleted": files_deleted}
        
    except Exception as e:
        logger.error("File cleanup failed", error=str(e))
        return {"error": str(e)}

# FastAPI Router
TaskOrchestratorRouter = APIRouter()

@TaskOrchestratorRouter.post("/generate-content")
async def trigger_content_generation(config: Dict[str, Any], background_tasks: BackgroundTasks):
    """Trigger content generation pipeline."""
    try:
        orchestrator = TaskOrchestrator()
        
        # Run pipeline in background
        background_tasks.add_task(
            orchestrator.orchestrate_content_pipeline,
            config
        )
        
        return {
            "status": "started",
            "message": "Content generation pipeline started",
            "config": config
        }
        
    except Exception as e:
        logger.error("Failed to trigger content generation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@TaskOrchestratorRouter.get("/tasks/status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a Celery task."""
    try:
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "info": result.info
        }
        
    except Exception as e:
        logger.error("Failed to get task status", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@TaskOrchestratorRouter.post("/tasks/schedule")
async def schedule_task(task_name: str, schedule_time: datetime, config: Dict[str, Any] = None):
    """Schedule a task for later execution."""
    try:
        if task_name == "generate_content":
            task = generate_daily_content.apply_async(eta=schedule_time)
        elif task_name == "update_analytics":
            task = update_analytics.apply_async(eta=schedule_time)
        elif task_name == "process_monetization":
            task = process_monetization.apply_async(eta=schedule_time)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown task: {task_name}")
        
        return {
            "task_id": task.id,
            "task_name": task_name,
            "scheduled_for": schedule_time.isoformat(),
            "status": "scheduled"
        }
        
    except Exception as e:
        logger.error("Failed to schedule task", task_name=task_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))