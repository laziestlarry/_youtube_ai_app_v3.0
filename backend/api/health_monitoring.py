from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging
from ..monitoring.health_monitor import health_monitor
from ..models.responses import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Monitoring"])

@router.get("/api/v1/status", response_model=APIResponse)
async def get_health_status():
    """Get overall system health status."""
    try:
        health_summary = health_monitor.get_health_summary()
        
        return APIResponse(
            status="success",
            data=health_summary,
            message="Health status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving health status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/components", response_model=APIResponse)
async def get_all_components():
    """Get health status of all system components."""
    try:
        components_data = {}
        
        for component_name in health_monitor.components.keys():
            component_details = health_monitor.get_component_details(component_name)
            if component_details:
                components_data[component_name] = component_details
        
        return APIResponse(
            status="success",
            data={"components": components_data},
            message="Component health data retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving component health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/components/{component_name}", response_model=APIResponse)
async def get_component_health(component_name: str):
    """Get detailed health information for a specific component."""
    try:
        component_details = health_monitor.get_component_details(component_name)
        
        if not component_details:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
        
        return APIResponse(
            status="success",
            data=component_details,
            message=f"Component '{component_name}' health data retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving component health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/metrics/{metric_name}/history", response_model=APIResponse)
async def get_metric_history(
    metric_name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve (1-168)")
):
    """Get historical data for a specific metric."""
    try:
        history_data = health_monitor.get_metrics_history(metric_name, hours)
        
        return APIResponse(
            status="success",
            data={
                "metric_name": metric_name,
                "hours": hours,
                "data_points": len(history_data),
                "history": history_data
            },
            message=f"Metric history for '{metric_name}' retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving metric history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/alerts", response_model=APIResponse)
async def get_recent_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours of alerts to retrieve (1-168)")
):
    """Get recent health alerts."""
    try:
        alerts = health_monitor.get_recent_alerts(hours)
        
        # Group alerts by component
        alerts_by_component = {}
        for alert in alerts:
            component = alert["component"]
            if component not in alerts_by_component:
                alerts_by_component[component] = []
            alerts_by_component[component].append(alert)
        
        return APIResponse(
            status="success",
            data={
                "total_alerts": len(alerts),
                "hours": hours,
                "alerts": alerts,
                "alerts_by_component": alerts_by_component
            },
            message=f"Retrieved {len(alerts)} alerts from the last {hours} hours"
        )
    except Exception as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/check", response_model=APIResponse)
async def trigger_health_check():
    """Manually trigger a health check."""
    try:
        await health_monitor.perform_health_checks()
        
        health_summary = health_monitor.get_health_summary()
        
        return APIResponse(
            status="success",
            data=health_summary,
            message="Health check completed successfully"
        )
    except Exception as e:
        logger.error(f"Error performing health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/metrics/summary", response_model=APIResponse)
async def get_metrics_summary():
    """Get a summary of all current metrics."""
    try:
        summary = {}
        
        for component_name, component in health_monitor.components.items():
            component_metrics = {}
            for metric in component.metrics:
                component_metrics[metric.name] = {
                    "value": metric.value,
                    "status": metric.status,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp
                }
            summary[component_name] = component_metrics
        
        return APIResponse(
            status="success",
            data={"metrics_summary": summary},
            message="Metrics summary retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving metrics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/alerts/clear", response_model=APIResponse)
async def clear_old_alerts(
    days: int = Query(7, ge=1, le=30, description="Clear alerts older than this many days")
):
    """Clear old alerts and metrics data."""
    try:
        health_monitor.clear_old_data(days)
        
        return APIResponse(
            status="success",
            data={"cleared_days": days},
            message=f"Cleared health data older than {days} days"
        )
    except Exception as e:
        logger.error(f"Error clearing old data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/uptime", response_model=APIResponse)
async def get_system_uptime():
    """Get system uptime information."""
    try:
        import psutil
        import time
        
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_days = uptime_seconds / 86400
        
        uptime_info = {
            "boot_time": datetime.fromtimestamp(boot_time),
            "uptime_seconds": uptime_seconds,
            "uptime_days": uptime_days,
            "uptime_formatted": f"{int(uptime_days)}d {int((uptime_seconds % 86400) / 3600)}h {int((uptime_seconds % 3600) / 60)}m"
        }
        
        return APIResponse(
            status="success",
            data=uptime_info,
            message="System uptime retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving system uptime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/performance", response_model=APIResponse)
async def get_performance_metrics():
    """Get current performance metrics."""
    try:
        import psutil
        
        # Get current system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        performance_data = {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True)
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_gb": disk.used / (1024**3),
                "usage_percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "processes": {
                "total": len(psutil.pids()),
                "running": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running'])
            }
        }
        
        return APIResponse(
            status="success",
            data=performance_data,
            message="Performance metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/diagnostics", response_model=APIResponse)
async def run_system_diagnostics():
    """Run comprehensive system diagnostics."""
    try:
        diagnostics = {
            "timestamp": datetime.now(),
            "system_info": {},
            "health_checks": {},
            "recommendations": []
        }
        
        # System information
        import platform
        import psutil
        
        diagnostics["system_info"] = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "disk_total_gb": psutil.disk_usage('/').total / (1024**3)
        }
        
        # Run health checks
        await health_monitor.perform_health_checks()
        
        # Collect health check results
        for component_name, component in health_monitor.components.items():
            diagnostics["health_checks"][component_name] = {
                "status": component.status,
                "metrics": len(component.metrics),
                "errors": component.error_count,
                "last_error": component.last_error
            }
        
        # Generate recommendations
        recommendations = []
        
        # Check for unhealthy components
        unhealthy_components = [
            name for name, comp in health_monitor.components.items() 
            if comp.status == "unhealthy"
        ]
        if unhealthy_components:
            recommendations.append({
                "type": "critical",
                "message": f"Unhealthy components detected: {', '.join(unhealthy_components)}",
                "action": "Investigate and resolve component issues immediately"
            })
        
        # Check for degraded components
        degraded_components = [
            name for name, comp in health_monitor.components.items() 
            if comp.status == "degraded"
        ]
        if degraded_components:
            recommendations.append({
                "type": "warning",
                "message": f"Degraded components detected: {', '.join(degraded_components)}",
                "action": "Monitor closely and consider optimization"
            })
        
        # Check system resources
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            recommendations.append({
                "type": "warning",
                "message": f"High memory usage: {memory.percent:.1f}%",
                "action": "Consider increasing memory or optimizing memory usage"
            })
        
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            recommendations.append({
                "type": "warning",
                "message": f"High CPU usage: {cpu_percent:.1f}%",
                "action": "Investigate high CPU processes and optimize"
            })
        
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            recommendations.append({
                "type": "critical",
                "message": f"Low disk space: {disk_percent:.1f}% used",
                "action": "Free up disk space immediately"
            })
        elif disk_percent > 80:
            recommendations.append({
                "type": "warning",
                "message": f"Disk space getting low: {disk_percent:.1f}% used",
                "action": "Plan for disk cleanup or expansion"
            })
        
        diagnostics["recommendations"] = recommendations
        
        return APIResponse(
            status="success",
            data=diagnostics,
            message="System diagnostics completed successfully"
        )
    except Exception as e:
        logger.error(f"Error running system diagnostics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))