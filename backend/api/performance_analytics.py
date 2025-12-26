from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timedelta
import logging
from ..analytics.performance_analytics import performance_analytics
from ..models.responses import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/performance", tags=["Performance Analytics"])

@router.post("/api/v1/metrics/record", response_model=APIResponse)
async def record_performance_metric(
    metric_name: str,
    value: float,
    component: str,
    tags: Optional[dict] = None
):
    """Record a performance metric."""
    try:
        await performance_analytics.record_metric(
            metric_name=metric_name,
            value=value,
            component=component,
            tags=tags
        )
        
        return APIResponse(
            status="success",
            data={
                "metric_name": metric_name,
                "value": value,
                "component": component,
                "timestamp": datetime.now().isoformat()
            },
            message="Performance metric recorded successfully"
        )
    except Exception as e:
        logger.error(f"Error recording performance metric: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/metrics/{component}/{metric_name}/history", response_model=APIResponse)
async def get_metric_history(
    component: str,
    metric_name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve")
):
    """Get historical data for a specific metric."""
    try:
        metrics = await performance_analytics.get_metrics_history(
            component=component,
            metric_name=metric_name,
            hours=hours
        )
        
        # Convert to serializable format
        metrics_data = [
            {
                "timestamp": m.timestamp.isoformat(),
                "value": m.value,
                "tags": m.tags
            }
            for m in metrics
        ]
        
        return APIResponse(
            status="success",
            data={
                "component": component,
                "metric_name": metric_name,
                "time_period": f"{hours}h",
                "data_points": len(metrics_data),
                "metrics": metrics_data
            },
            message="Metric history retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving metric history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/analysis/{component}/{metric_name}", response_model=APIResponse)
async def analyze_metric_performance(
    component: str,
    metric_name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of data to analyze")
):
    """Analyze performance for a specific metric."""
    try:
        analysis = await performance_analytics.analyze_performance(
            component=component,
            metric_name=metric_name,
            hours=hours
        )
        
        return APIResponse(
            status="success",
            data=analysis.__dict__,
            message="Performance analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"Error analyzing metric performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/components/{component}/summary", response_model=APIResponse)
async def get_component_performance_summary(
    component: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of data to analyze")
):
    """Get comprehensive performance summary for a component."""
    try:
        summary = await performance_analytics.get_component_performance_summary(
            component=component,
            hours=hours
        )
        
        return APIResponse(
            status="success",
            data=summary,
            message=f"Component performance summary for {component} retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting component performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/system/overview", response_model=APIResponse)
async def get_system_performance_overview(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to analyze")
):
    """Get system-wide performance overview."""
    try:
        overview = await performance_analytics.get_system_performance_overview(hours=hours)
        
        return APIResponse(
            status="success",
            data=overview,
            message="System performance overview retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting system performance overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/export", response_model=APIResponse)
async def export_performance_data(
    component: Optional[str] = None,
    metric_name: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168, description="Hours of data to export"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format")
):
    """Export performance data for analysis."""
    try:
        export_data = await performance_analytics.export_performance_data(
            component=component,
            metric_name=metric_name,
            hours=hours,
            format=format
        )
        
        return APIResponse(
            status="success",
            data=export_data,
            message="Performance data exported successfully"
        )
    except Exception as e:
        logger.error(f"Error exporting performance data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup", response_model=APIResponse)
async def cleanup_old_performance_data(
    background_tasks: BackgroundTasks,
    days: int = Query(30, ge=1, le=365, description="Delete data older than this many days")
):
    """Clean up old performance metrics data."""
    try:
        # Run cleanup in background
        background_tasks.add_task(performance_analytics.cleanup_old_metrics, days)
        
        return APIResponse(
            status="success",
            data={"cleanup_days": days},
            message=f"Performance data cleanup scheduled for data older than {days} days"
        )
    except Exception as e:
        logger.error(f"Error scheduling performance data cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/metrics/list", response_model=APIResponse)
async def list_available_metrics(
    component: Optional[str] = None
):
    """List all available performance metrics."""
    try:
        from ..database import get_db_connection
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(days=7)  # Last 7 days
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if component:
                cursor.execute("""
                    SELECT DISTINCT metric_name, component, COUNT(*) as data_points,
                           MIN(timestamp) as first_recorded, MAX(timestamp) as last_recorded
                    FROM performance_metrics
                    WHERE component = ? AND timestamp > ?
                    GROUP BY metric_name, component
                    ORDER BY component, metric_name
                """, (component, cutoff_time.isoformat()))
            else:
                cursor.execute("""
                    SELECT DISTINCT metric_name, component, COUNT(*) as data_points,
                           MIN(timestamp) as first_recorded, MAX(timestamp) as last_recorded
                    FROM performance_metrics
                    WHERE timestamp > ?
                    GROUP BY metric_name, component
                    ORDER BY component, metric_name
                """, (cutoff_time.isoformat(),))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "metric_name": row[0],
                    "component": row[1],
                    "data_points": row[2],
                    "first_recorded": row[3],
                    "last_recorded": row[4]
                })
        
        return APIResponse(
            status="success",
            data={
                "metrics": metrics,
                "total_metrics": len(metrics),
                "filter_component": component
            },
            message="Available metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing available metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/alerts/performance", response_model=APIResponse)
async def get_performance_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back for alerts"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$")
):
    """Get performance-based alerts and anomalies."""
    try:
        from ..database import get_db_connection
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get all components with recent data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT component
                FROM performance_metrics
                WHERE timestamp > ?
            """, (cutoff_time.isoformat(),))
            
            components = [row[0] for row in cursor.fetchall()]
        
        alerts = []
        
        # Analyze each component for alerts
        for component in components:
            try:
                summary = await performance_analytics.get_component_performance_summary(
                    component, hours
                )
                
                # Generate alerts based on health score and anomalies
                if summary["health_score"] < 50:
                    alerts.append({
                        "id": f"health_{component}_{int(datetime.now().timestamp())}",
                        "type": "health_score",
                        "severity": "critical",
                        "component": component,
                        "message": f"{component} health score is critically low: {summary['health_score']:.1f}",
                        "timestamp": datetime.now().isoformat(),
                        "details": {
                            "health_score": summary["health_score"],
                            "metrics_with_issues": summary["summary"]["metrics_with_issues"]
                        }
                    })
                elif summary["health_score"] < 70:
                    alerts.append({
                        "id": f"health_{component}_{int(datetime.now().timestamp())}",
                        "type": "health_score",
                        "severity": "high",
                        "component": component,
                        "message": f"{component} health score needs attention: {summary['health_score']:.1f}",
                        "timestamp": datetime.now().isoformat(),
                        "details": {
                            "health_score": summary["health_score"],
                            "metrics_with_issues": summary["summary"]["metrics_with_issues"]
                        }
                    })
                
                # Check for anomalies in individual metrics
                for metric_name, analysis in summary["metric_analyses"].items():
                    high_severity_anomalies = [
                        a for a in analysis["anomalies"] 
                        if a.get("severity") == "high"
                    ]
                    
                    if high_severity_anomalies:
                        alerts.append({
                            "id": f"anomaly_{component}_{metric_name}_{int(datetime.now().timestamp())}",
                            "type": "anomaly",
                            "severity": "high",
                            "component": component,
                            "metric": metric_name,
                            "message": f"High-severity anomalies detected in {metric_name}",
                            "timestamp": datetime.now().isoformat(),
                            "details": {
                                "anomaly_count": len(high_severity_anomalies),
                                "latest_anomaly": high_severity_anomalies[-1]
                            }
                        })
            
            except Exception as e:
                logger.error(f"Error analyzing component {component} for alerts: {str(e)}")
                continue
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        # Sort by severity and timestamp
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: (severity_order.get(x["severity"], 4), x["timestamp"]), reverse=True)
        
        return APIResponse(
            status="success",
            data={
                "alerts": alerts,
                "total_alerts": len(alerts),
                "time_period": f"{hours}h",
                "severity_filter": severity
            },
            message="Performance alerts retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting performance alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/benchmarks/run", response_model=APIResponse)
async def run_performance_benchmark(
    background_tasks: BackgroundTasks,
    component: str,
    benchmark_type: str = Query(..., regex="^(load|stress|endurance)$"),
    duration_minutes: int = Query(5, ge=1, le=60)
):
    """Run performance benchmarks for a component."""
    try:
        benchmark_id = f"benchmark_{component}_{benchmark_type}_{int(datetime.now().timestamp())}"
        
        # Schedule benchmark in background
        background_tasks.add_task(
            _run_benchmark_task,
            benchmark_id,
            component,
            benchmark_type,
            duration_minutes
        )
        
        return APIResponse(
            status="success",
            data={
                "benchmark_id": benchmark_id,
                "component": component,
                "benchmark_type": benchmark_type,
                "duration_minutes": duration_minutes,
                "status": "scheduled"
            },
            message="Performance benchmark scheduled successfully"
        )
    except Exception as e:
        logger.error(f"Error scheduling performance benchmark: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _run_benchmark_task(
    benchmark_id: str,
    component: str,
    benchmark_type: str,
    duration_minutes: int
):
    """Run a performance benchmark task."""
    try:
        import asyncio
        import random
        
        logger.info(f"Starting benchmark {benchmark_id} for {component}")
        
        # Record benchmark start
        await performance_analytics.record_metric(
            metric_name="benchmark_status",
            value=1.0,  # 1 = running
            component=component,
            tags={
                "benchmark_id": benchmark_id,
                "benchmark_type": benchmark_type,
                "status": "started"
            }
        )
        
        # Simulate benchmark execution
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            # Simulate different benchmark types
            if benchmark_type == "load":
                # Simulate load testing metrics
                response_time = random.uniform(50, 200)  # ms
                throughput = random.uniform(100, 500)    # requests/sec
                cpu_usage = random.uniform(30, 70)       # %
                
                await performance_analytics.record_metric("response_time", response_time, component, {"benchmark_id": benchmark_id})
                await performance_analytics.record_metric("throughput", throughput, component, {"benchmark_id": benchmark_id})
                await performance_analytics.record_metric("cpu_usage", cpu_usage, component, {"benchmark_id": benchmark_id})
                
            elif benchmark_type == "stress":
                # Simulate stress testing metrics
                response_time = random.uniform(100, 1000)  # ms
                error_rate = random.uniform(0, 10)         # %
                memory_usage = random.uniform(50, 90)      # %
                
                await performance_analytics.record_metric("response_time", response_time, component, {"benchmark_id": benchmark_id})
                await performance_analytics.record_metric("error_rate", error_rate, component, {"benchmark_id": benchmark_id})
                await performance_analytics.record_metric("memory_usage", memory_usage, component, {"benchmark_id": benchmark_id})
                
            elif benchmark_type == "endurance":
                # Simulate endurance testing metrics
                response_time = random.uniform(80, 300)    # ms
                memory_usage = random.uniform(40, 80)      # %
                connection_count = random.uniform(10, 100) # connections
                
                await performance_analytics.record_metric("response_time", response_time, component, {"benchmark_id": benchmark_id})
                await performance_analytics.record_metric("memory_usage", memory_usage, component, {"benchmark_id": benchmark_id})
                await performance_analytics.record_metric("connection_count", connection_count, component, {"benchmark_id": benchmark_id})
            
            # Wait before next measurement
            await asyncio.sleep(10)  # 10 second intervals
        
        # Record benchmark completion
        await performance_analytics.record_metric(
            metric_name="benchmark_status",
            value=0.0,  # 0 = completed
            component=component,
            tags={
                "benchmark_id": benchmark_id,
                "benchmark_type": benchmark_type,
                "status": "completed",
                "duration_minutes": duration_minutes
            }
        )
        
        logger.info(f"Completed benchmark {benchmark_id} for {component}")
        
    except Exception as e:
        logger.error(f"Error running benchmark {benchmark_id}: {str(e)}")
        
        # Record benchmark failure
        try:
            await performance_analytics.record_metric(
                metric_name="benchmark_status",
                value=-1.0,  # -1 = failed
                component=component,
                tags={
                    "benchmark_id": benchmark_id,
                    "benchmark_type": benchmark_type,
                    "status": "failed",
                    "error": str(e)
                }
            )
        except:
            pass

@router.get("/api/v1/benchmarks/{benchmark_id}/results", response_model=APIResponse)
async def get_benchmark_results(benchmark_id: str):
    """Get results from a performance benchmark."""
    try:
        from ..database import get_db_connection
        import json
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, metric_name, value, component, tags
                FROM performance_metrics
                WHERE tags LIKE ?
                ORDER BY timestamp ASC
            """, (f'%"benchmark_id": "{benchmark_id}"%',))
            
            results = []
            component = None
            benchmark_type = None
            
            for row in cursor.fetchall():
                tags = json.loads(row[4]) if row[4] else {}
                if tags.get("benchmark_id") == benchmark_id:
                    results.append({
                        "timestamp": row[0],
                        "metric_name": row[1],
                        "value": row[2],
                        "component": row[3],
                        "tags": tags
                    })
                    
                    if not component:
                        component = row[3]
                    if not benchmark_type and "benchmark_type" in tags:
                        benchmark_type = tags["benchmark_type"]
        
        if not results:
            raise HTTPException(status_code=404, detail="Benchmark results not found")
        
        # Analyze benchmark results
        metrics_summary = {}
        for result in results:
            metric_name = result["metric_name"]
            if metric_name not in metrics_summary:
                metrics_summary[metric_name] = []
            metrics_summary[metric_name].append(result["value"])
        
        # Calculate statistics for each metric
        statistics_summary = {}
        for metric_name, values in metrics_summary.items():
            if metric_name != "benchmark_status":  # Skip status metric
                import statistics
                statistics_summary[metric_name] = {
                    "count": len(values),
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return APIResponse(
            status="success",
            data={
                "benchmark_id": benchmark_id,
                "component": component,
                "benchmark_type": benchmark_type,
                "total_data_points": len(results),
                "raw_results": results,
                "statistics": statistics_summary
            },
            message="Benchmark results retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting benchmark results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))