from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import logging
from pydantic import BaseModel, Field

from ..config.enhanced_settings import settings, QualityLevel, ContentType
from ..ai_modules.management_engine import management_engine
from ..ai_modules.content_scheduler import content_scheduler
from ..ai_modules.analytics_engine import analytics_engine
from ..database import get_db_connection
from ..utils.response_models import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2", tags=["Enhanced API"])

# Request Models
class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., description="Content topic")
    content_type: ContentType = Field(ContentType.EDUCATIONAL, description="Type of content")
    quality_level: QualityLevel = Field(QualityLevel.MEDIUM, description="Quality level")
    target_duration: int = Field(600, description="Target duration in seconds")
    target_audience: str = Field("general", description="Target audience")
    monetization_enabled: bool = Field(True, description="Enable monetization")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions")
    model_type: Optional[str] = Field("openai", description="AI model to use (openai, llama3, mistral, gemini, groq)")
    endpoint: Optional[str] = Field("cloud", description="Inference endpoint (cloud, local, web, network)")

class SchedulingRequest(BaseModel):
    frequency: str = Field("daily", description="Scheduling frequency")
    content_types: List[ContentType] = Field([ContentType.EDUCATIONAL], description="Content types")
    quality_level: QualityLevel = Field(QualityLevel.MEDIUM, description="Quality level")
    target_views: int = Field(10000, description="Target views")
    posting_times: List[int] = Field([9, 15, 18], description="Preferred posting hours")
    auto_publish: bool = Field(False, description="Auto-publish content")

class AnalyticsRequest(BaseModel):
    start_date: Optional[datetime] = Field(None, description="Start date for analytics")
    end_date: Optional[datetime] = Field(None, description="End date for analytics")
    metrics: List[str] = Field(["views", "engagement", "revenue"], description="Metrics to include")
    granularity: str = Field("daily", description="Data granularity")
    include_predictions: bool = Field(False, description="Include future predictions")

class OptimizationRequest(BaseModel):
    content_id: Optional[str] = Field(None, description="Specific content ID to optimize")
    optimization_type: str = Field("all", description="Type of optimization")
    target_metric: str = Field("engagement", description="Target metric to optimize")
    aggressive_mode: bool = Field(False, description="Use aggressive optimization")

# Enhanced Content Generation
@router.post("/api/v1/content/generate")
async def generate_enhanced_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate content with enhanced AI capabilities."""
    try:
        # Validate request
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        # Get quality settings
        quality_settings = settings.get_quality_settings(request.quality_level)
        
        # Create generation task
        task_id = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start background generation
        background_tasks.add_task(
            _generate_content_background,
            task_id,
            request,
            quality_settings
        )
        
        return APIResponse(
            status="success",
            data={
                "task_id": task_id,
                "estimated_completion": datetime.now() + timedelta(minutes=30),
                "quality_settings": quality_settings
            },
            message="Content generation started"
        )
        
    except Exception as e:
        logger.error(f"Error starting content generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_content_background(
    task_id: str,
    request: ContentGenerationRequest,
    quality_settings: Dict[str, Any]
):
    """Background task for content generation."""
    try:
        # Initialize pipeline with enhanced settings
        from ..ai_modules.video_pipeline_enhanced import EnhancedVideoPipeline
        
        # Pass model_type and endpoint to pipeline
        pipeline = EnhancedVideoPipeline(
            topic=request.topic,
            title=f"AI Generated: {request.topic}",
            quality_level=request.quality_level.value,
            monetization_enabled=request.monetization_enabled,
            model_type=getattr(request, 'model_type', 'openai'),
            endpoint=getattr(request, 'endpoint', 'cloud')
        )
        
        # Execute pipeline
        result = await pipeline.execute_full_pipeline()
        
        # Store result
        await _store_generation_result(task_id, result)
        
        # Send notification if enabled
        if settings.notifications.enabled:
            await _send_completion_notification(task_id, result)
            
    except Exception as e:
        logger.error(f"Background generation failed for {task_id}: {str(e)}")
        await _store_generation_error(task_id, str(e))

# Enhanced Scheduling
@router.post("/api/v1/scheduling/setup")
async def setup_enhanced_scheduling(request: SchedulingRequest):
    """Setup enhanced content scheduling."""
    try:
        # Validate scheduling request
        if request.frequency not in ["daily", "weekly", "monthly"]:
            raise HTTPException(status_code=400, detail="Invalid frequency")
        
        # Setup scheduling with enhanced parameters
        schedule_config = {
            "frequency": request.frequency,
            "content_types": [ct.value for ct in request.content_types],
            "quality_level": request.quality_level.value,
            "target_views": request.target_views,
            "posting_times": request.posting_times,
            "auto_publish": request.auto_publish,
            "timezone": settings.scheduling.timezone
        }
        
        result = await content_scheduler.setup_enhanced_scheduling(schedule_config)
        
        return APIResponse(
            status="success",
            data=result,
            message="Enhanced scheduling configured successfully"
        )
        
    except Exception as e:
        logger.error(f"Error setting up scheduling: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Real-time Analytics
@router.get("/api/v1/analytics/realtime")
async def get_realtime_analytics():
    """Get real-time analytics data."""
    try:
        if not settings.analytics.real_time_enabled:
            raise HTTPException(status_code=403, detail="Real-time analytics disabled")
        
        # Get real-time metrics
        metrics = await analytics_engine.get_realtime_metrics()
        
        return APIResponse(
            status="success",
            data=metrics,
            message="Real-time analytics retrieved"
        )
        
    except Exception as e:
        logger.error(f"Error getting real-time analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Analytics with Predictions
@router.post("/api/v1/analytics/comprehensive")
async def get_comprehensive_analytics(request: AnalyticsRequest):
    """Get comprehensive analytics with predictions."""
    try:
        # Set default date range if not provided
        if not request.start_date:
            request.start_date = datetime.now() - timedelta(days=30)
        if not request.end_date:
            request.end_date = datetime.now()
        
        # Get comprehensive analytics
        analytics_data = await analytics_engine.get_comprehensive_analytics(
            start_date=request.start_date,
            end_date=request.end_date,
            metrics=request.metrics,
            granularity=request.granularity,
            include_predictions=request.include_predictions
        )
        
        return APIResponse(
            status="success",
            data=analytics_data,
            message="Comprehensive analytics retrieved"
        )
        
    except Exception as e:
        logger.error(f"Error getting comprehensive analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI-Powered Optimization
@router.post("/api/v1/optimization/ai-optimize")
async def ai_optimize_content(request: OptimizationRequest):
    """AI-powered content optimization."""
    try:
        # Perform AI optimization
        optimization_result = await management_engine.ai_optimize_content(
            content_id=request.content_id,
            optimization_type=request.optimization_type,
            target_metric=request.target_metric,
            aggressive_mode=request.aggressive_mode
        )
        
        return APIResponse(
            status="success",
            data=optimization_result,
            message="AI optimization completed"
        )
        
    except Exception as e:
        logger.error(f"Error in AI optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Health and Monitoring
@router.get("/api/v1/system/health")
async def get_system_health():
    """Get comprehensive system health status."""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "components": {
                "database": await _check_database_health(),
                "cache": await _check_cache_health(),
                "ai_services": await _check_ai_services_health(),
                "storage": await _check_storage_health(),
                "scheduler": await _check_scheduler_health()
            },
            "performance_metrics": {
                "response_time": await _get_average_response_time(),
                "throughput": await _get_current_throughput(),
                "error_rate": await _get_error_rate(),
                "resource_usage": await _get_resource_usage()
            },
            "feature_flags": settings.get_feature_flags(),
            "configuration_issues": settings.validate_config()
        }
        
        # Determine overall health status
        unhealthy_components = [k for k, v in health_data["components"].items() if not v]
        if unhealthy_components:
            health_data["status"] = "degraded" if len(unhealthy_components) < 3 else "unhealthy"
        
        return APIResponse(
            status="success",
            data=health_data,
            message="System health retrieved"
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration Management
@router.get("/api/v1/config/current")
async def get_current_configuration():
    """Get current system configuration."""
    try:
        config_data = {
            "feature_flags": settings.get_feature_flags(),
            "quality_levels": [level.value for level in QualityLevel],
            "content_types": [ct.value for ct in ContentType],
            "storage_provider": settings.storage.provider,
            "cache_enabled": settings.cache.enabled,
            "monetization_enabled": settings.monetization.enabled,
            "scheduling_enabled": settings.scheduling.enabled,
            "analytics_enabled": settings.analytics.enabled
        }
        
        return APIResponse(
            status="success",
            data=config_data,
            message="Configuration retrieved"
        )
        
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/config/update")
async def update_configuration(config_updates: Dict[str, Any]):
    """Update system configuration."""
    try:
        # Validate configuration updates
        validation_errors = []
        
        for section, updates in config_updates.items():
            if not hasattr(settings, section):
                validation_errors.append(f"Unknown configuration section: {section}")
                continue
            
            config_obj = getattr(settings, section)
            for key, value in updates.items():
                if not hasattr(config_obj, key):
                    validation_errors.append(f"Unknown configuration key: {section}.{key}")
        
        if validation_errors:
            raise HTTPException(status_code=400, detail=validation_errors)
        
        # Apply configuration updates
        for section, updates in config_updates.items():
            config_obj = getattr(settings, section)
            for key, value in updates.items():
                setattr(config_obj, key, value)
        
        # Save configuration
        settings.save_config()
        
        # Validate updated configuration
        issues = settings.validate_config()
        
        return APIResponse(
            status="success",
            data={
                "updated_sections": list(config_updates.keys()),
                "validation_issues": issues
            },
            message="Configuration updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch Operations
@router.post("/api/v1/batch/process")
async def process_batch_operations(
    operations: List[Dict[str, Any]],
    background_tasks: BackgroundTasks
):
    """Process multiple operations in batch."""
    try:
        if not settings.ai.batch_processing_enabled:
            raise HTTPException(status_code=403, detail="Batch processing disabled")
        
        if len(operations) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size too large (max 50)")
        
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start batch processing in background
        background_tasks.add_task(_process_batch_background, batch_id, operations)
        
        return APIResponse(
            status="success",
            data={
                "batch_id": batch_id,
                "operation_count": len(operations),
                "estimated_completion": datetime.now() + timedelta(minutes=len(operations) * 2)
            },
            message="Batch processing started"
        )
        
    except Exception as e:
        logger.error(f"Error starting batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Export Data
@router.get("/api/v1/export/analytics")
async def export_analytics_data(
    format: str = Query("json", description="Export format (json, csv, xlsx)"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Export analytics data in various formats."""
    try:
        if not settings.analytics.export_enabled:
            raise HTTPException(status_code=403, detail="Data export disabled")
        
        # Set default date range
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Get analytics data
        analytics_data = await analytics_engine.get_export_data(start_date, end_date)
        
        # Format data based on requested format
        if format.lower() == "json":
            return APIResponse(
                status="success",
                data=analytics_data,
                message="Analytics data exported as JSON"
            )
        elif format.lower() == "csv":
            csv_data = await _convert_to_csv(analytics_data)
            return StreamingResponse(
                iter([csv_data]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=analytics.csv"}
            )
        elif format.lower() == "xlsx":
            xlsx_data = await _convert_to_xlsx(analytics_data)
            return StreamingResponse(
                iter([xlsx_data]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=analytics.xlsx"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for Real-time Updates
@router.websocket("/ws/realtime")
async def websocket_realtime_updates(websocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    
    try:
        while True:
            # Get real-time data
            realtime_data = await analytics_engine.get_realtime_metrics()
            
            # Send data to client
            await websocket.send_json({
                "type": "realtime_update",
                "data": realtime_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait before next update
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

# Helper Functions
async def _check_database_health() -> bool:
    """Check database health."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception:
        return False

async def _check_cache_health() -> bool:
    """Check cache health."""
    try:
        if not settings.cache.enabled:
            return True
        # Add cache health check logic here
        return True
    except Exception:
        return False

async def _check_ai_services_health() -> bool:
    """Check AI services health."""
    try:
        # Add AI services health check logic here
        return bool(settings.ai.openai_api_key)
    except Exception:
        return False

async def _check_storage_health() -> bool:
    """Check storage health."""
    try:
        # Add storage health check logic here
        return True
    except Exception:
        return False

async def _check_scheduler_health() -> bool:
    """Check scheduler health."""
    try:
        return settings.scheduling.enabled and len(content_scheduler.scheduled_tasks) >= 0
    except Exception:
        return False

async def _get_average_response_time() -> float:
    """Get average response time."""
    # Implement response time tracking
    return 0.5  # Placeholder

async def _get_current_throughput() -> int:
    """Get current throughput."""
    # Implement throughput tracking
    return 100  # Placeholder

async def _get_error_rate() -> float:
    """Get current error rate."""
    # Implement error rate tracking
    return 0.01  # Placeholder

async def _get_resource_usage() -> Dict[str, float]:
    """Get resource usage metrics."""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }

async def _store_generation_result(task_id: str, result: Dict[str, Any]):
    """Store generation result."""
    # Implement result storage logic
    pass

async def _store_generation_error(task_id: str, error: str):
    """Store generation error."""
    # Implement error storage logic
    pass

async def _send_completion_notification(task_id: str, result: Dict[str, Any]):
    """Send completion notification."""
    # Implement notification logic
    pass

async def _process_batch_background(batch_id: str, operations: List[Dict[str, Any]]):
    """Process batch operations in background."""
    try:
        results = []
        for i, operation in enumerate(operations):
            try:
                # Process individual operation
                result = await _process_single_operation(operation)
                results.append({"index": i, "status": "success", "result": result})
            except Exception as e:
                results.append({"index": i, "status": "error", "error": str(e)})
        
        # Store batch results
        await _store_batch_results(batch_id, results)
        
    except Exception as e:
        logger.error(f"Batch processing failed for {batch_id}: {str(e)}")

async def _process_single_operation(operation: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single operation."""
    operation_type = operation.get("type")
    
    if operation_type == "generate_content":
        # Handle content generation
        pass
    elif operation_type == "optimize_content":
        # Handle content optimization
        pass
    elif operation_type == "schedule_content":
        # Handle content scheduling
        pass
    else:
        raise ValueError(f"Unknown operation type: {operation_type}")
    
    return {"processed": True}

async def _store_batch_results(batch_id: str, results: List[Dict[str, Any]]):
    """Store batch processing results."""
    # Implement batch results storage
    pass

async def _convert_to_csv(data: Dict[str, Any]) -> str:
    """Convert data to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    # Implement CSV conversion logic
    return output.getvalue()

async def _convert_to_xlsx(data: Dict[str, Any]) -> bytes:
    """Convert data to XLSX format."""
    import openpyxl
    import io
    
    # Implement XLSX conversion logic
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    
    # Add data to worksheet
    # ... implementation details
    
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()