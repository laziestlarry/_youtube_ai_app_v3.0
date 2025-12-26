from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .database_enhanced import db_manager
from .ai_modules.content_scheduler_enhanced import get_scheduler
from .ai_modules.video_pipeline_enhanced import EnhancedVideoPipeline
from .utils.security import SecurityManager
from .utils.cache import CacheManager
from .utils.monitoring import SystemMonitor

logger = logging.getLogger(__name__)

# Initialize components
security_manager = SecurityManager()
cache_manager = CacheManager()
system_monitor = SystemMonitor()
security = HTTPBearer()

app = FastAPI(
    title="YouTube AI Content Platform",
    description="Enhanced AI-powered YouTube content generation and management platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class InitializationRequest(BaseModel):
    channel_id: str = Field(..., min_length=1, description="YouTube channel ID")
    api_key: str = Field(..., min_length=1, description="YouTube API key")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")

class SchedulingRequest(BaseModel):
    frequency: str = Field(..., description="Content frequency: daily, weekly, monthly")
    category: str = Field(..., description="Content category")
    target_views: int = Field(default=10000, ge=1, description="Target view count")
    monetization_enabled: bool = Field(default=True, description="Enable monetization")
    auto_publish: bool = Field(default=False, description="Auto-publish content")
    quality_level: str = Field(default="high", description="Quality level: low, medium, high")
    content_themes: List[str] = Field(default_factory=list, description="Content themes")

class PipelineRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Video topic")
    title: str = Field(..., min_length=1, description="Video title")
    target_views: int = Field(default=10000, ge=1, description="Target views")
    monetization_enabled: bool = Field(default=True, description="Enable monetization")
    quality_level: str = Field(default="high", description="Quality level")

class TaskUpdateRequest(BaseModel):
    status: str = Field(..., description="New task status")
    scheduled_time: Optional[datetime] = Field(None, description="New scheduled time")

# Response models
class APIResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate user authentication."""
    try:
        # In production, implement proper JWT validation
        token = credentials.credentials
        user_data = await security_manager.validate_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

async def rate_limit_check(request: Request):
    """Check rate limiting."""
    client_ip = request.client.host
    if not await security_manager.check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return True

# Health and status endpoints
@app.get("/health")
async def health_check():
    """System health check."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": await db_manager.health_check(),
                "scheduler": await (await get_scheduler()).health_check(),
                "cache": cache_manager.health_check(),
                "system": system_monitor.get_system_health()
            }
        }
        
        # Overall health based on components
        all_healthy = all(health_status["components"].values())
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/status")
async def get_system_status():
    """Get detailed system status."""
    try:
        scheduler = await get_scheduler()
        
        status_data = {
            "system": {
                "uptime": system_monitor.get_uptime(),
                "cpu_usage": system_monitor.get_cpu_usage(),
                "memory_usage": system_monitor.get_memory_usage(),
                "disk_usage": system_monitor.get_disk_usage()
            },
            "database": await db_manager.get_database_stats(),
            "scheduler": await scheduler.get_scheduler_stats(),
            "cache": cache_manager.get_stats(),
            "security": await security_manager.get_security_stats()
        }
        
        return APIResponse(
            status="success",
            data=status_data,
            message="System status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialization endpoints
@app.post("/api/initialize")
async def initialize_system(
    request: InitializationRequest,
    background_tasks: BackgroundTasks,
    _: bool = Depends(rate_limit_check)
):
    """Initialize the system with user configuration."""
    try:
        logger.info(f"Initializing system for channel: {request.channel_id}")
        
        # Validate API key (in production, make actual API call)
        if len(request.api_key) < 10:
            raise HTTPException(status_code=400, detail="Invalid API key format")
        
        # Store user configuration
        config_data = {
            "api_key_hash": security_manager.hash_api_key(request.api_key),
            "preferences": request.preferences,
            "features": {
                "monetization": True,
                "auto_scheduling": True,
                "quality_level": "high"
            }
        }
        
        await db_manager.store_user_config(request.channel_id, config_data)
        
        # Initialize monitoring for the channel
        monitoring_config = {
            "channel_id": request.channel_id,
            "metrics_enabled": True,
            "alert_thresholds": {
                "low_performance": 0.3,
                "high_error_rate": 0.1
            }
        }
        
        await db_manager.store_monitoring_config(request.channel_id, monitoring_config)
        
        # Schedule background initialization tasks
        background_tasks.add_task(
            _background_initialization,
            request.channel_id,
            request.preferences
        )
        
        return APIResponse(
            status="success",
            data={
                "channel_id": request.channel_id,
                "initialization_status": "started",
                "features_enabled": list(config_data["features"].keys())
            },
            message="System initialization started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

async def _background_initialization(channel_id: str, preferences: Dict[str, Any]):
    """Background initialization tasks."""
    try:
        # Simulate initialization tasks
        await asyncio.sleep(2)
        
        # Update user config status
        config_data = {
            "preferences": preferences,
            "features": {
                "monetization": True,
                "auto_scheduling": True,
                "quality_level": "high"
            }
        }
        
        await db_manager.store_user_config(channel_id, config_data)
        
        logger.info(f"Background initialization completed for {channel_id}")
        
    except Exception as e:
        logger.error(f"Background initialization failed: {e}")

# Content scheduling endpoints
@app.post("/api/schedule-content")
async def schedule_content(
    request: SchedulingRequest,
    channel_id: str,
    background_tasks: BackgroundTasks,
    _: bool = Depends(rate_limit_check)
):
    """Schedule automated content generation."""
    try:
        scheduler = await get_scheduler()
        
        # Create scheduling configuration
        from .ai_modules.content_scheduler_enhanced import SchedulingConfig
        
        config = SchedulingConfig(
            frequency=request.frequency,
            category=request.category,
            target_views=request.target_views,
            monetization_enabled=request.monetization_enabled,
            auto_publish=request.auto_publish,
            quality_level=request.quality_level,
            content_themes=request.content_themes
        )
        
        # Schedule content
        result = await scheduler.schedule_content(channel_id, config)
        
        return APIResponse(
            status="success",
            data=result,
            message="Content scheduling completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Content scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scheduled-tasks")
async def get_scheduled_tasks(
    channel_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get scheduled content tasks."""
    try:
        scheduler = await get_scheduler()
        tasks = await scheduler.get_scheduled_tasks(channel_id, status)
        
        # Limit results
        if limit:
            tasks = tasks[:limit]
        
        return APIResponse(
            status="success",
            data={
                "tasks": tasks,
                "total_count": len(tasks),
                "filters": {
                    "channel_id": channel_id,
                    "status": status
                }
            },
            message="Scheduled tasks retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get scheduled tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/scheduled-tasks/{task_id}")
async def update_scheduled_task(
    task_id: str,
    request: TaskUpdateRequest,
    _: bool = Depends(rate_limit_check)
):
    """Update a scheduled task."""
    try:
        scheduler = await get_scheduler()
        
        if request.status == "cancelled":
            success = await scheduler.cancel_task(task_id)
        elif request.scheduled_time:
            success = await scheduler.reschedule_task(task_id, request.scheduled_time)
        else:
            # Update status only
            await db_manager.update_scheduled_content_status(task_id, request.status)
            success = True
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return APIResponse(
            status="success",
            data={"task_id": task_id, "updated_status": request.status},
            message="Task updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pipeline execution endpoints
@app.post("/api/execute-pipeline")
async def execute_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    _: bool = Depends(rate_limit_check)
):
    """Execute video generation pipeline."""
    try:
        # Create pipeline instance
        pipeline = EnhancedVideoPipeline(
            topic=request.topic,
            title=request.title,
            target_views=request.target_views,
            monetization_enabled=request.monetization_enabled,
            quality_level=request.quality_level
        )
        
        # Execute pipeline in background
        background_tasks.add_task(_execute_pipeline_background, pipeline)
        
        return APIResponse(
            status="success",
            data={
                "pipeline_id": pipeline.pipeline_id,
                "status": "started",
                "estimated_completion": "10-15 minutes"
            },
            message="Pipeline execution started"
        )
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _execute_pipeline_background(pipeline: EnhancedVideoPipeline):
    """Execute pipeline in background."""
    try:
        result = await pipeline.execute_full_pipeline()
        logger.info(f"Pipeline completed: {pipeline.pipeline_id} - Success: {result.success}")
    except Exception as e:
        logger.error(f"Background pipeline execution failed: {e}")

@app.get("/api/pipeline/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str):
    """Get pipeline execution status."""
    try:
        # Get from database
        pipeline_data = await db_manager.get_pipeline_result(pipeline_id)
        
        if not pipeline_data:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        return APIResponse(
            status="success",
            data=pipeline_data,
            message="Pipeline status retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and optimization endpoints
@app.get("/api/v1/analytics/performance")
async def get_performance_analytics(
    entity_type: str,
    entity_id: str,
    metric_name: Optional[str] = None,
    limit: int = 100
):
    """Get performance analytics."""
    try:
        metrics = await db_manager.get_performance_metrics(
            entity_type, entity_id, metric_name, limit
        )
        
        # Calculate summary statistics
        if metrics:
            values = [m["metric_value"] for m in metrics]
            summary = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
        else:
            summary = {"count": 0}
        
        return APIResponse(
            status="success",
            data={
                "metrics": metrics,
                "summary": summary,
                "entity_type": entity_type,
                "entity_id": entity_id
            },
            message="Performance analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/optimize-schedule")
async def optimize_schedule(
    channel_id: str,
    _: bool = Depends(rate_limit_check)
):
    """Optimize content schedule based on performance data."""
    try:
        scheduler = await get_scheduler()
        optimization_result = await scheduler.optimize_schedule(channel_id)
        
        return APIResponse(
            status="success",
            data=optimization_result,
            message="Schedule optimization completed"
        )
        
    except Exception as e:
        logger.error(f"Schedule optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Security and monitoring endpoints
@app.get("/api/security/events")
async def get_security_events(
    limit: int = 100,
    severity: Optional[str] = None
):
    """Get security events."""
    try:
        events = await db_manager.get_security_events(limit, severity)
        
        return APIResponse(
            status="success",
            data={
                "events": events,
                "total_count": len(events),
                "severity_filter": severity
            },
            message="Security events retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Security events retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/security/report")
async def report_security_event(
    event_type: str,
    severity: str,
    details: str,
    request: Request
):
    """Report a security event."""
    try:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")
        
        event_data = {
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow()
        }
        
        await db_manager.store_security_event(event_data)
        
        # Trigger security response if high severity
        if severity in ["high", "critical"]:
            await security_manager.handle_security_incident(event_data)
        
        return APIResponse(
            status="success",
            data={"event_id": event_data.get("id")},
            message="Security event reported successfully"
        )
        
    except Exception as e:
        logger.error(f"Security event reporting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cache management endpoints
@app.delete("/api/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = None,
    _: bool = Depends(rate_limit_check)
):
    """Clear system cache."""
    try:
        if cache_type:
            result = cache_manager.clear_cache_type(cache_type)
        else:
            result = cache_manager.clear_all_cache()
        
        return APIResponse(
            status="success",
            data={"cleared": result},
            message="Cache cleared successfully"
        )
        
    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = cache_manager.get_detailed_stats()
        
        return APIResponse(
            status="success",
            data=stats,
            message="Cache statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Cache stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch operations endpoints
@app.post("/api/batch/schedule-content")
async def batch_schedule_content(
    requests: List[SchedulingRequest],
    channel_id: str,
    background_tasks: BackgroundTasks,
    _: bool = Depends(rate_limit_check)
):
    """Schedule multiple content items in batch."""
    try:
        if len(requests) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size too large (max 50)")
        
        scheduler = await get_scheduler()
        results = []
        
        for i, request in enumerate(requests):
            try:
                from .ai_modules.content_scheduler_enhanced import SchedulingConfig
                
                config = SchedulingConfig(
                    frequency=request.frequency,
                    category=request.category,
                    target_views=request.target_views,
                    monetization_enabled=request.monetization_enabled,
                    auto_publish=request.auto_publish,
                    quality_level=request.quality_level,
                    content_themes=request.content_themes
                )
                
                result = await scheduler.schedule_content(f"{channel_id}_batch_{i}", config)
                results.append({"index": i, "status": "success", "data": result})
                
            except Exception as e:
                results.append({"index": i, "status": "error", "error": str(e)})
        
        success_count = sum(1 for r in results if r["status"] == "success")
        
        return APIResponse(
            status="success",
            data={
                "results": results,
                "summary": {
                    "total": len(requests),
                    "successful": success_count,
                    "failed": len(requests) - success_count
                }
            },
            message=f"Batch scheduling completed: {success_count}/{len(requests)} successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch/execute-pipelines")
async def batch_execute_pipelines(
    requests: List[PipelineRequest],
    background_tasks: BackgroundTasks,
    _: bool = Depends(rate_limit_check)
):
    """Execute multiple pipelines in batch."""
    try:
        if len(requests) > 10:  # Limit batch size for pipelines
            raise HTTPException(status_code=400, detail="Batch size too large (max 10)")
        
        pipeline_ids = []
        
        for request in requests:
            pipeline = EnhancedVideoPipeline(
                topic=request.topic,
                title=request.title,
                target_views=request.target_views,
                monetization_enabled=request.monetization_enabled,
                quality_level=request.quality_level
            )
            
            pipeline_ids.append(pipeline.pipeline_id)
            background_tasks.add_task(_execute_pipeline_background, pipeline)
        
        return APIResponse(
            status="success",
            data={
                "pipeline_ids": pipeline_ids,
                "batch_size": len(requests),
                "estimated_completion": "15-30 minutes"
            },
            message="Batch pipeline execution started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export and import endpoints
@app.get("/api/export/data")
async def export_data(
    channel_id: str,
    data_type: str,
    format: str = "json",
    _: bool = Depends(rate_limit_check)
):
    """Export system data."""
    try:
        if data_type == "scheduled_tasks":
            data = await db_manager.get_scheduled_content(channel_id=channel_id)
        elif data_type == "performance_metrics":
            data = await db_manager.get_performance_metrics("channel", channel_id, limit=1000)
        elif data_type == "pipeline_results":
            data = await db_manager.get_pipeline_results(channel_id=channel_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        export_data = {
            "channel_id": channel_id,
            "data_type": data_type,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        return APIResponse(
            status="success",
            data=export_data,
            message="Data exported successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoints for real-time updates
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.channel_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if channel_id:
            if channel_id not in self.channel_subscriptions:
                self.channel_subscriptions[channel_id] = []
            self.channel_subscriptions[channel_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, channel_id: str = None):
        self.active_connections.remove(websocket)
        
        if channel_id and channel_id in self.channel_subscriptions:
            if websocket in self.channel_subscriptions[channel_id]:
                self.channel_subscriptions[channel_id].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_channel(self, message: str, channel_id: str):
        if channel_id in self.channel_subscriptions:
            for connection in self.channel_subscriptions[channel_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.channel_subscriptions[channel_id].remove(connection)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: str):
    await manager.connect(websocket, channel_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            message_data = json.loads(data)
            
            if message_data.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)

# Utility function to send real-time updates
async def send_pipeline_update(pipeline_id: str, channel_id: str, status_data: Dict[str, Any]):
    """Send pipeline status update via WebSocket."""
    try:
        message = json.dumps({
            "type": "pipeline_update",
            "pipeline_id": pipeline_id,
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await manager.broadcast_to_channel(message, channel_id)
        
    except Exception as e:
        logger.error(f"Failed to send pipeline update: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return APIResponse(
        status="error",
        data={"status_code": exc.status_code},
        message=exc.detail
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    
    return APIResponse(
        status="error",
        data={"error_type": type(exc).__name__},
        message="An internal server error occurred"
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        logger.info("Starting YouTube AI Content Platform...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Initialize scheduler
        scheduler = await get_scheduler()
        
        # Initialize monitoring
        system_monitor.start_monitoring()
        
        logger.info("Platform startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        logger.info("Shutting down YouTube AI Content Platform...")
        
        # Shutdown scheduler
        if enhanced_scheduler:
            await enhanced_scheduler.shutdown()
        
        # Stop monitoring
        system_monitor.stop_monitoring()
        
        # Close database connections
        await db_manager.close()
        
        logger.info("Platform shutdown completed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")