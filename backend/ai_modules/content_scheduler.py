from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta
import asyncio
from backend.models import APIResponse
from backend.database import log_execution
from backend.youtube_logic import generate_ideas
from backend.ai_modules.task_orchestrator import VideoPipeline
import json
import random

logger = logging.getLogger(__name__)
router = APIRouter()

class ContentScheduler:
    def __init__(self):
        self.scheduled_tasks = {}
        self.content_calendar = {}
        self.growth_metrics = {
            "views": [],
            "engagement": [],
            "earnings": []
        }
    
    async def schedule_content_generation(self, 
                                        frequency: str = "daily",
                                        category: str = "tech",
                                        target_views: int = 10000,
                                        monetization_enabled: bool = True):
        """
        Schedule automated content generation based on frequency and category.
        
        Args:
            frequency (str): 'daily', 'weekly', or 'monthly'
            category (str): Content category
            target_views (int): Target view count
            monetization_enabled (bool): Whether to enable monetization
        """
        try:
            # Generate content ideas
            ideas = generate_ideas(category, n=5)
            
            # Schedule each idea
            for idea in ideas:
                if isinstance(idea, dict):
                    title = idea['title']
                    expected_views = idea['expected_views']
                else:
                    title = idea
                    expected_views = random.randint(1000, 5000)
                
                # Calculate posting time based on frequency
                posting_time = self._calculate_posting_time(frequency)
                
                # Schedule the content
                task_id = f"task_{len(self.scheduled_tasks)}"
                self.scheduled_tasks[task_id] = {
                    "title": title,
                    "category": category,
                    "expected_views": expected_views,
                    "posting_time": posting_time,
                    "monetization_enabled": monetization_enabled,
                    "status": "scheduled"
                }
                
                # Log the scheduled task
                log_execution(
                    "content_scheduling",
                    "success",
                    {
                        "task_id": task_id,
                        "title": title,
                        "posting_time": posting_time.isoformat()
                    }
                )
            
            return {
                "scheduled_tasks": self.scheduled_tasks,
                "message": f"Successfully scheduled {len(ideas)} content pieces"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error scheduling content: {str(e)}"
            )
    
    def _calculate_posting_time(self, frequency: str) -> datetime:
        """Calculate optimal posting time based on frequency."""
        now = datetime.now()
        
        if frequency == "daily":
            # Post at 3 PM local time
            return now.replace(hour=15, minute=0, second=0, microsecond=0)
        elif frequency == "weekly":
            # Post on Wednesday at 3 PM
            days_ahead = (2 - now.weekday()) % 7
            return (now + timedelta(days=days_ahead)).replace(hour=15, minute=0, second=0, microsecond=0)
        else:  # monthly
            # Post on the 15th at 3 PM
            if now.day >= 15:
                next_month = now.replace(day=1) + timedelta(days=32)
                return next_month.replace(day=15, hour=15, minute=0, second=0, microsecond=0)
            else:
                return now.replace(day=15, hour=15, minute=0, second=0, microsecond=0)
    
    async def execute_scheduled_task(self, task_id: str):
        """Execute a scheduled content generation task."""
        if task_id not in self.scheduled_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = self.scheduled_tasks[task_id]
        try:
            # Create video pipeline
            pipeline = VideoPipeline(
                topic=task["category"],
                title=task["title"],
                monetization_enabled=task["monetization_enabled"]
            )
            
            # Execute pipeline
            video_path = await pipeline.full_run()
            
            # Update task status
            task["status"] = "completed"
            task["video_path"] = video_path
            
            # Log execution
            log_execution(
                "content_execution",
                "success",
                {
                    "task_id": task_id,
                    "video_path": video_path
                }
            )
            
            return {
                "status": "success",
                "video_path": video_path,
                "message": "Content generated and uploaded successfully"
            }
            
        except Exception as e:
            task["status"] = "failed"
            logger.error(f"Error executing task {task_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error executing task: {str(e)}"
            )
    
    def get_growth_strategy(self, current_metrics: Dict[str, List[float]]) -> Dict[str, any]:
        """
        Generate growth strategy based on current metrics.
        
        Args:
            current_metrics (Dict[str, List[float]]): Current performance metrics
            
        Returns:
            Dict[str, any]: Growth strategy recommendations
        """
        strategy = {
            "content_frequency": self._calculate_optimal_frequency(current_metrics),
            "best_categories": self._identify_best_categories(current_metrics),
            "monetization_strategy": self._generate_monetization_strategy(current_metrics),
            "growth_targets": self._set_growth_targets(current_metrics)
        }
        
        return strategy
    
    def _calculate_optimal_frequency(self, metrics: Dict[str, List[float]]) -> str:
        """Calculate optimal posting frequency based on metrics."""
        if not metrics["views"]:
            return "weekly"
        
        avg_views = sum(metrics["views"]) / len(metrics["views"])
        if avg_views > 10000:
            return "daily"
        elif avg_views > 5000:
            return "weekly"
        else:
            return "monthly"
    
    def _identify_best_categories(self, metrics: Dict[str, List[float]]) -> List[str]:
        """Identify best performing categories."""
        # This would typically come from a database
        return ["tech", "gaming", "education"]
    
    def _generate_monetization_strategy(self, metrics: Dict[str, List[float]]) -> Dict[str, any]:
        """Generate monetization strategy based on metrics."""
        return {
            "ad_placement": "strategic",
            "sponsorship_threshold": 5000,
            "merchandise_launch": "when_views_exceed_10000",
            "affiliate_marketing": "recommended"
        }
    
    def _set_growth_targets(self, metrics: Dict[str, List[float]]) -> Dict[str, any]:
        """Set realistic growth targets based on current performance."""
        if not metrics["views"]:
            return {
                "views_target": 1000,
                "engagement_target": 5,
                "earnings_target": 100
            }
        
        current_views = metrics["views"][-1]
        return {
            "views_target": int(current_views * 1.5),
            "engagement_target": 8,
            "earnings_target": int(current_views * 0.01)  # $0.01 per view
        }

# Initialize scheduler
content_scheduler = ContentScheduler()

@router.post("/schedule-content", response_model=APIResponse)
async def schedule_content_endpoint(
    frequency: str = "daily",
    category: str = "tech",
    target_views: int = 10000,
    monetization_enabled: bool = True
):
    """
    Schedule automated content generation.
    
    Args:
        frequency (str): Content generation frequency
        category (str): Content category
        target_views (int): Target view count
        monetization_enabled (bool): Whether to enable monetization
        
    Returns:
        APIResponse: Scheduling results
    """
    try:
        result = await content_scheduler.schedule_content_generation(
            frequency,
            category,
            target_views,
            monetization_enabled
        )
        
        return APIResponse(
            status="success",
            data=result,
            message="Content scheduled successfully"
        )
        
    except Exception as e:
        logger.error(f"Error scheduling content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error scheduling content: {str(e)}"
        )

@router.post("/execute-task/{task_id}", response_model=APIResponse)
async def execute_task_endpoint(task_id: str):
    """
    Execute a scheduled content generation task.
    
    Args:
        task_id (str): Task identifier
        
    Returns:
        APIResponse: Execution results
    """
    try:
        result = await content_scheduler.execute_scheduled_task(task_id)
        
        return APIResponse(
            status="success",
            data=result,
            message="Task executed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing task: {str(e)}"
        )

@router.get("/growth-strategy", response_model=APIResponse)
async def get_growth_strategy_endpoint():
    """
    Get growth strategy recommendations.
    
    Returns:
        APIResponse: Growth strategy
    """
    try:
        strategy = content_scheduler.get_growth_strategy(content_scheduler.growth_metrics)
        
        return APIResponse(
            status="success",
            data=strategy,
            message="Growth strategy generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating growth strategy: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating growth strategy: {str(e)}"
        ) 