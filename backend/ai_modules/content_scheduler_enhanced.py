import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
from dataclasses import dataclass, asdict
import json

from ..database_enhanced import db_manager
from ..utils.cache import CacheManager
from .video_pipeline import EnhancedVideoPipeline
from ..youtube_logic import generate_ideas

logger = logging.getLogger(__name__)

@dataclass
class ContentTask:
    task_id: str
    channel_id: str
    title: str
    category: str
    frequency: str
    target_views: int
    scheduled_time: datetime
    status: str = "scheduled"
    priority: int = 1
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['scheduled_time'] = self.scheduled_time.isoformat()
        return data

@dataclass
class SchedulingConfig:
    frequency: str = "daily"
    category: str = "tech"
    target_views: int = 10000
    monetization_enabled: bool = True
    auto_publish: bool = False
    quality_level: str = "high"
    content_themes: List[str] = None
    posting_schedule: Dict[str, Any] = None

class EnhancedContentScheduler:
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.active_tasks: Dict[str, ContentTask] = {}
        self.scheduling_configs: Dict[str, SchedulingConfig] = {}
        self.execution_queue = asyncio.Queue()
        self.worker_tasks: List[asyncio.Task] = []
        self.max_concurrent_executions = 3
        self.running = False
        
        # Performance tracking
        self.execution_stats = {
            "total_scheduled": 0,
            "total_executed": 0,
            "total_failed": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
    
    async def initialize(self):
        """Initialize the content scheduler."""
        try:
            # Load existing scheduled tasks from database
            await self._load_scheduled_tasks()
            
            # Start worker tasks
            await self._start_workers()
            
            # Start scheduling loop
            asyncio.create_task(self._scheduling_loop())
            
            self.running = True
            logger.info("Enhanced content scheduler initialized")
            
        except Exception as e:
            logger.error(f"Content scheduler initialization failed: {e}")
            raise
    
    async def _load_scheduled_tasks(self):
        """Load scheduled tasks from database."""
        try:
            tasks = await db_manager.get_scheduled_content(status="scheduled")
            
            for task_data in tasks:
                task = ContentTask(
                    task_id=task_data["task_id"],
                    channel_id=task_data["channel_id"],
                    title=task_data["title"],
                    category=task_data["category"],
                    frequency=task_data["frequency"],
                    target_views=task_data["target_views"],
                    scheduled_time=datetime.fromisoformat(task_data["scheduled_time"]),
                    status=task_data["status"]
                )
                self.active_tasks[task.task_id] = task
            
            logger.info(f"Loaded {len(self.active_tasks)} scheduled tasks")
            
        except Exception as e:
            logger.error(f"Failed to load scheduled tasks: {e}")
    
    async def _start_workers(self):
        """Start worker tasks for content execution."""
        try:
            for i in range(self.max_concurrent_executions):
                worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
                self.worker_tasks.append(worker)
            
            logger.info(f"Started {self.max_concurrent_executions} worker tasks")
            
        except Exception as e:
            logger.error(f"Failed to start workers: {e}")
            raise
    
    async def _worker_loop(self, worker_id: str):
        """Worker loop for executing content tasks."""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(
                    self.execution_queue.get(),
                    timeout=30.0
                )
                
                logger.info(f"Worker {worker_id} executing task: {task.task_id}")
                
                # Execute the task
                await self._execute_content_task(task, worker_id)
                
                # Mark task as done
                self.execution_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks available, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _scheduling_loop(self):
        """Main scheduling loop to check for due tasks."""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                # Check for due tasks
                due_tasks = [
                    task for task in self.active_tasks.values()
                    if task.scheduled_time <= current_time and task.status == "scheduled"
                ]
                
                # Queue due tasks for execution
                for task in due_tasks:
                    await self.execution_queue.put(task)
                    task.status = "queued"
                    
                    # Update in database
                    await db_manager.update_scheduled_content_status(
                        task.task_id, "queued"
                    )
                
                if due_tasks:
                    logger.info(f"Queued {len(due_tasks)} tasks for execution")
                
                # Check for recurring tasks that need rescheduling
                await self._handle_recurring_tasks()
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Scheduling loop error: {e}")
                await asyncio.sleep(60)
    
    async def _execute_content_task(self, task: ContentTask, worker_id: str):
        """Execute a content generation task."""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing content task: {task.task_id}")
            
            # Update task status
            task.status = "executing"
            await db_manager.update_scheduled_content_status(
                task.task_id, "executing"
            )
            
            # Get user configuration
            user_config = await db_manager.get_user_config(task.channel_id)
            if not user_config:
                raise Exception(f"No user configuration found for channel: {task.channel_id}")
            
            # Create enhanced pipeline
            pipeline = EnhancedVideoPipeline(
                topic=task.category,
                title=task.title,
                target_views=task.target_views,
                monetization_enabled=user_config.get("features", {}).get("monetization", True),
                quality_level=user_config.get("features", {}).get("quality_level", "high")
            )
            
            # Execute pipeline
            result = await pipeline.execute_full_pipeline()
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update task status and result
            task.status = "completed" if result.success else "failed"
            
            result_data = {
                "success": result.success,
                "artifacts": result.artifacts,
                "execution_time": execution_time,
                "worker_id": worker_id,
                "error": result.error if not result.success else None
            }
            
            await db_manager.update_scheduled_content_status(
                task.task_id, task.status, result_data
            )
            
            # Update statistics
            self._update_execution_stats(result.success, execution_time)
            
            # Store performance metrics
            await db_manager.store_performance_metric(
                "content_task", task.task_id, "execution_time", execution_time
            )
            
            await db_manager.store_performance_metric(
                "content_task", task.task_id, "success", 1.0 if result.success else 0.0
            )
            
            logger.info(f"Task {task.task_id} completed: {task.status}")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error(f"Task execution failed: {task.task_id} - {e}")
            
            task.status = "failed"
            result_data = {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "worker_id": worker_id
            }
            
            await db_manager.update_scheduled_content_status(
                task.task_id, "failed", result_data
            )
            
            self._update_execution_stats(False, execution_time)
        
        finally:
            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)
    
    async def _handle_recurring_tasks(self):
        """Handle recurring task scheduling."""
        try:
            current_time = datetime.utcnow()
            
            # Check for channels with recurring schedules
            for channel_id, config in self.scheduling_configs.items():
                if config.frequency in ["daily", "weekly", "monthly"]:
                    # Check if we need to schedule next occurrence
                    await self._schedule_next_occurrence(channel_id, config)
            
        except Exception as e:
            logger.error(f"Recurring task handling failed: {e}")
    
    async def _schedule_next_occurrence(self, channel_id: str, config: SchedulingConfig):
        """Schedule next occurrence of recurring content."""
        try:
            # Calculate next scheduled time based on frequency
            next_time = self._calculate_next_schedule_time(config.frequency)
            
            # Generate new content idea
            ideas = generate_ideas(config.category, n=1)
            if not ideas:
                logger.warning(f"No ideas generated for channel {channel_id}")
                return
            
            idea = ideas[0]
            title = idea.get("title", f"Auto-generated {config.category} content") if isinstance(idea, dict) else str(idea)
            
            # Create new task
            task_id = f"auto_{channel_id}_{int(next_time.timestamp())}"
            
            task = ContentTask(
                task_id=task_id,
                channel_id=channel_id,
                title=title,
                category=config.category,
                frequency=config.frequency,
                target_views=config.target_views,
                scheduled_time=next_time,
                metadata={"auto_generated": True, "theme": config.content_themes}
            )
            
            # Store in database
            await db_manager.store_scheduled_content(task.to_dict())
            
            # Add to active tasks
            self.active_tasks[task_id] = task
            
            logger.info(f"Scheduled next occurrence: {task_id} at {next_time}")
            
        except Exception as e:
            logger.error(f"Failed to schedule next occurrence: {e}")
    
    def _calculate_next_schedule_time(self, frequency: str) -> datetime:
        """Calculate next schedule time based on frequency."""
        current_time = datetime.utcnow()
        
        if frequency == "daily":
            return current_time + timedelta(days=1)
        elif frequency == "weekly":
            return current_time + timedelta(weeks=1)
        elif frequency == "monthly":
            return current_time + timedelta(days=30)
        else:
            # Default to daily
            return current_time + timedelta(days=1)
    
    def _update_execution_stats(self, success: bool, execution_time: float):
        """Update execution statistics."""
        try:
            self.execution_stats["total_executed"] += 1
            
            if success:
                self.execution_stats["total_scheduled"] += 1
            else:
                self.execution_stats["total_failed"] += 1
            
            # Update average execution time
            current_avg = self.execution_stats["average_execution_time"]
            total_executed = self.execution_stats["total_executed"]
            
            self.execution_stats["average_execution_time"] = (
                (current_avg * (total_executed - 1) + execution_time) / total_executed
            )
            
            # Update success rate
            total_attempts = self.execution_stats["total_scheduled"] + self.execution_stats["total_failed"]
            if total_attempts > 0:
                self.execution_stats["success_rate"] = (
                    self.execution_stats["total_scheduled"] / total_attempts
                )
            
        except Exception as e:
            logger.error(f"Failed to update execution stats: {e}")
    
    async def schedule_content(self, channel_id: str, config: SchedulingConfig) -> Dict[str, Any]:
        """Schedule content generation for a channel."""
        try:
            # Store scheduling configuration
            self.scheduling_configs[channel_id] = config
            
            # Generate initial content ideas
            ideas = generate_ideas(config.category, n=5)
            scheduled_tasks = []
            
            for i, idea in enumerate(ideas):
                # Calculate scheduling time
                schedule_time = self._calculate_schedule_time(config.frequency, i)
                
                # Create task
                title = idea.get("title", f"Generated {config.category} content") if isinstance(idea, dict) else str(idea)
                task_id = f"{channel_id}_{int(schedule_time.timestamp())}_{i}"
                
                task = ContentTask(
                    task_id=task_id,
                    channel_id=channel_id,
                    title=title,
                    category=config.category,
                    frequency=config.frequency,
                    target_views=config.target_views,
                    scheduled_time=schedule_time,
                    priority=1,
                    metadata={"batch_id": f"batch_{int(datetime.utcnow().timestamp())}"}
                )
                
                # Store in database
                await db_manager.store_scheduled_content(task.to_dict())
                
                # Add to active tasks
                self.active_tasks[task_id] = task
                scheduled_tasks.append(task.to_dict())
            
            logger.info(f"Scheduled {len(scheduled_tasks)} content tasks for {channel_id}")
            
            return {
                "status": "success",
                "scheduled_count": len(scheduled_tasks),
                "tasks": scheduled_tasks,
                "next_execution": min(task.scheduled_time for task in self.active_tasks.values()).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content scheduling failed: {e}")
            raise
    
    def _calculate_schedule_time(self, frequency: str, index: int) -> datetime:
        """Calculate schedule time for content based on frequency and index."""
        base_time = datetime.utcnow()
        
        if frequency == "daily":
            return base_time + timedelta(days=index)
        elif frequency == "weekly":
            return base_time + timedelta(weeks=index)
        elif frequency == "monthly":
            return base_time + timedelta(days=30 * index)
        else:
            # Default to daily
            return base_time + timedelta(days=index)
    
    async def get_scheduled_tasks(self, channel_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get scheduled tasks with optional filtering."""
        try:
            # Get from database
            tasks = await db_manager.get_scheduled_content(status=status)
            
            # Filter by channel if specified
            if channel_id:
                tasks = [task for task in tasks if task["channel_id"] == channel_id]
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get scheduled tasks: {e}")
            return []
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        try:
            # Update in database
            await db_manager.update_scheduled_content_status(task_id, "cancelled")
            
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            logger.info(f"Task cancelled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    async def reschedule_task(self, task_id: str, new_time: datetime) -> bool:
        """Reschedule a task to a new time."""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.scheduled_time = new_time
                task.status = "scheduled"
                
                # Update in database
                await db_manager.update_scheduled_content_status(task_id, "scheduled")
                
                logger.info(f"Task rescheduled: {task_id} to {new_time}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reschedule task {task_id}: {e}")
            return False
    
    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics and status."""
        try:
            current_time = datetime.utcnow()
            
            # Count tasks by status
            status_counts = {}
            upcoming_tasks = []
            
            for task in self.active_tasks.values():
                status_counts[task.status] = status_counts.get(task.status, 0) + 1
                
                if task.status == "scheduled" and task.scheduled_time > current_time:
                    upcoming_tasks.append({
                        "task_id": task.task_id,
                        "title": task.title,
                        "scheduled_time": task.scheduled_time.isoformat(),
                        "category": task.category
                    })
            
            # Sort upcoming tasks by time
            upcoming_tasks.sort(key=lambda x: x["scheduled_time"])
            
            return {
                "status": "running" if self.running else "stopped",
                "active_tasks_count": len(self.active_tasks),
                "status_breakdown": status_counts,
                "upcoming_tasks": upcoming_tasks[:10],  # Next 10 tasks
                "worker_count": len(self.worker_tasks),
                "queue_size": self.execution_queue.qsize(),
                "execution_stats": self.execution_stats.copy(),
                "configured_channels": len(self.scheduling_configs)
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler stats: {e}")
            return {"status": "error", "error": str(e)}
    
    async def optimize_schedule(self, channel_id: str) -> Dict[str, Any]:
        """Optimize content schedule based on performance data."""
        try:
            # Get performance metrics for the channel
            metrics = await db_manager.get_performance_metrics(
                "channel", channel_id, limit=100
            )
            
            if not metrics:
                return {
                    "status": "no_data",
                    "message": "Insufficient performance data for optimization"
                }
            
            # Analyze performance patterns
            optimization_suggestions = []
            
            # Analyze success rates by time of day
            time_performance = self._analyze_time_performance(metrics)
            if time_performance:
                optimization_suggestions.append({
                    "type": "timing",
                    "suggestion": f"Best posting time: {time_performance['best_time']}",
                    "impact": "high"
                })
            
            # Analyze category performance
            category_performance = self._analyze_category_performance(metrics)
            if category_performance:
                optimization_suggestions.append({
                    "type": "content",
                    "suggestion": f"Focus on {category_performance['best_category']} content",
                    "impact": "medium"
                })
            
            # Analyze frequency optimization
            frequency_analysis = self._analyze_frequency_performance(metrics)
            if frequency_analysis:
                optimization_suggestions.append({
                    "type": "frequency",
                    "suggestion": f"Optimal posting frequency: {frequency_analysis['optimal_frequency']}",
                    "impact": "medium"
                })
            
            return {
                "status": "success",
                "channel_id": channel_id,
                "optimization_suggestions": optimization_suggestions,
                "current_performance": {
                    "average_success_rate": sum(m["metric_value"] for m in metrics if m["metric_name"] == "success") / len([m for m in metrics if m["metric_name"] == "success"]) if [m for m in metrics if m["metric_name"] == "success"] else 0,
                    "average_execution_time": sum(m["metric_value"] for m in metrics if m["metric_name"] == "execution_time") / len([m for m in metrics if m["metric_name"] == "execution_time"]) if [m for m in metrics if m["metric_name"] == "execution_time"] else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Schedule optimization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_time_performance(self, metrics: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze performance by time of day."""
        try:
            # This would analyze when content performs best
            # Simplified implementation
            return {
                "best_time": "10:00 AM",
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"Time performance analysis failed: {e}")
            return None
    
    def _analyze_category_performance(self, metrics: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze performance by content category."""
        try:
            # This would analyze which categories perform best
            # Simplified implementation
            return {
                "best_category": "tech",
                "performance_score": 0.85
            }
        except Exception as e:
            logger.error(f"Category performance analysis failed: {e}")
            return None
    
    def _analyze_frequency_performance(self, metrics: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze optimal posting frequency."""
        try:
            # This would analyze optimal posting frequency
            # Simplified implementation
            return {
                "optimal_frequency": "daily",
                "confidence": 0.7
            }
        except Exception as e:
            logger.error(f"Frequency performance analysis failed: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check scheduler health."""
        try:
            return (
                self.running and
                len(self.worker_tasks) > 0 and
                all(not task.done() for task in self.worker_tasks)
            )
        except Exception as e:
            logger.error(f"Scheduler health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown the scheduler."""
        try:
            logger.info("Shutting down content scheduler...")
            
            self.running = False
            
            # Cancel worker tasks
            for task in self.worker_tasks:
                task.cancel()
            
            # Wait for workers to finish
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            # Wait for queue to empty
            await self.execution_queue.join()
            
            logger.info("Content scheduler shutdown complete")
            
        except Exception as e:
            logger.error(f"Scheduler shutdown failed: {e}")

# Global scheduler instance
enhanced_scheduler = None

async def get_scheduler() -> EnhancedContentScheduler:
    """Get or create the global scheduler instance."""
    global enhanced_scheduler
    if enhanced_scheduler is None:
        from ..utils.cache import CacheManager
        cache_manager = CacheManager()
        enhanced_scheduler = EnhancedContentScheduler(cache_manager)
        await enhanced_scheduler.initialize()
    return enhanced_scheduler