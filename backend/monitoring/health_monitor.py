import asyncio
import psutil
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import aioredis
import sqlite3
from ..config.enhanced_settings import settings
from ..database import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    """Individual health metric data."""
    name: str
    value: float
    status: str  # healthy, warning, critical
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime
    unit: str = ""
    description: str = ""

@dataclass
class ComponentHealth:
    """Health status of a system component."""
    name: str
    status: str  # healthy, degraded, unhealthy
    metrics: List[HealthMetric]
    last_check: datetime
    uptime: float
    error_count: int = 0
    last_error: Optional[str] = None

class HealthMonitor:
    """Comprehensive system health monitoring."""
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring_active = False
        self.check_interval = settings.monitoring.health_check_interval
        
    async def start_monitoring(self):
        """Start the health monitoring loop."""
        self.monitoring_active = True
        logger.info("Health monitoring started")
        
        while self.monitoring_active:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop the health monitoring loop."""
        self.monitoring_active = False
        logger.info("Health monitoring stopped")
    
    async def perform_health_checks(self):
        """Perform all health checks."""
        try:
            # System resource checks
            await self.check_system_resources()
            
            # Database health check
            await self.check_database_health()
            
            # Cache health check (if enabled)
            if settings.cache.enabled:
                await self.check_cache_health()
            
            # AI service health check
            await self.check_ai_service_health()
            
            # Storage health check
            await self.check_storage_health()
            
            # Update overall system status
            self.update_overall_status()
            
            # Check for alerts
            await self.check_alerts()
            
        except Exception as e:
            logger.error(f"Error performing health checks: {str(e)}")
    
    async def check_system_resources(self):
        """Check system resource utilization."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metric = HealthMetric(
                name="cpu_usage",
                value=cpu_percent,
                status=self.get_status(cpu_percent, 70, 90),
                threshold_warning=70.0,
                threshold_critical=90.0,
                timestamp=datetime.now(),
                unit="%",
                description="CPU utilization percentage"
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_metric = HealthMetric(
                name="memory_usage",
                value=memory.percent,
                status=self.get_status(memory.percent, 80, 95),
                threshold_warning=80.0,
                threshold_critical=95.0,
                timestamp=datetime.now(),
                unit="%",
                description="Memory utilization percentage"
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_metric = HealthMetric(
                name="disk_usage",
                value=disk_percent,
                status=self.get_status(disk_percent, 85, 95),
                threshold_warning=85.0,
                threshold_critical=95.0,
                timestamp=datetime.now(),
                unit="%",
                description="Disk space utilization percentage"
            )
            
            # Network connections
            connections = len(psutil.net_connections())
            connection_metric = HealthMetric(
                name="network_connections",
                value=connections,
                status=self.get_status(connections, 1000, 2000),
                threshold_warning=1000.0,
                threshold_critical=2000.0,
                timestamp=datetime.now(),
                unit="connections",
                description="Number of active network connections"
            )
            
            # Update system component
            system_status = self.get_worst_status([cpu_metric, memory_metric, disk_metric, connection_metric])
            self.components["system"] = ComponentHealth(
                name="system",
                status=system_status,
                metrics=[cpu_metric, memory_metric, disk_metric, connection_metric],
                last_check=datetime.now(),
                uptime=time.time() - psutil.boot_time()
            )
            
            # Store metrics history
            for metric in [cpu_metric, memory_metric, disk_metric, connection_metric]:
                self.metrics_history[metric.name].append({
                    "timestamp": metric.timestamp,
                    "value": metric.value,
                    "status": metric.status
                })
                
        except Exception as e:
            logger.error(f"Error checking system resources: {str(e)}")
            self.components["system"] = ComponentHealth(
                name="system",
                status="unhealthy",
                metrics=[],
                last_check=datetime.now(),
                uptime=0,
                error_count=1,
                last_error=str(e)
            )
    
    async def check_database_health(self):
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test database connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                # Check database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0] if cursor.fetchone() else 0
                
                # Check table count
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Create metrics
            response_metric = HealthMetric(
                name="db_response_time",
                value=response_time,
                status=self.get_status(response_time, 100, 500),  # 100ms warning, 500ms critical
                threshold_warning=100.0,
                threshold_critical=500.0,
                timestamp=datetime.now(),
                unit="ms",
                description="Database query response time"
            )
            
            size_metric = HealthMetric(
                name="db_size",
                value=db_size / (1024 * 1024),  # Convert to MB
                status="healthy",  # Size is informational
                threshold_warning=1000.0,  # 1GB
                threshold_critical=5000.0,  # 5GB
                timestamp=datetime.now(),
                unit="MB",
                description="Database size in megabytes"
            )
            
            tables_metric = HealthMetric(
                name="db_tables",
                value=table_count,
                status="healthy",
                threshold_warning=100.0,
                threshold_critical=200.0,
                timestamp=datetime.now(),
                unit="tables",
                description="Number of database tables"
            )
            
            # Update database component
            db_status = self.get_worst_status([response_metric, size_metric, tables_metric])
            self.components["database"] = ComponentHealth(
                name="database",
                status=db_status,
                metrics=[response_metric, size_metric, tables_metric],
                last_check=datetime.now(),
                uptime=time.time()  # Assume database uptime equals system uptime
            )
            
            # Store metrics history
            for metric in [response_metric, size_metric, tables_metric]:
                self.metrics_history[metric.name].append({
                    "timestamp": metric.timestamp,
                    "value": metric.value,
                    "status": metric.status
                })
                
        except Exception as e:
            logger.error(f"Error checking database health: {str(e)}")
            self.components["database"] = ComponentHealth(
                name="database",
                status="unhealthy",
                metrics=[],
                last_check=datetime.now(),
                uptime=0,
                error_count=1,
                last_error=str(e)
            )
    
    async def check_cache_health(self):
        """Check Redis cache connectivity and performance."""
        try:
            start_time = time.time()
            
            # Connect to Redis
            redis = aioredis.from_url(settings.cache.redis_url)
            
            # Test basic operations
            await redis.set("health_check", "test", ex=60)
            result = await redis.get("health_check")
            await redis.delete("health_check")
            
            response_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = await redis.info()
            memory_usage = info.get('used_memory', 0) / (1024 * 1024)  # Convert to MB
            connected_clients = info.get('connected_clients', 0)
            
            await redis.close()
            
            # Create metrics
            response_metric = HealthMetric(
                name="cache_response_time",
                value=response_time,
                status=self.get_status(response_time, 50, 200),
                threshold_warning=50.0,
                threshold_critical=200.0,
                timestamp=datetime.now(),
                unit="ms",
                description="Cache operation response time"
            )
            
            memory_metric = HealthMetric(
                name="cache_memory",
                value=memory_usage,
                status=self.get_status(memory_usage, 500, 1000),  # 500MB warning, 1GB critical
                threshold_warning=500.0,
                threshold_critical=1000.0,
                timestamp=datetime.now(),
                unit="MB",
                description="Cache memory usage"
            )
            
            clients_metric = HealthMetric(
                name="cache_clients",
                value=connected_clients,
                status=self.get_status(connected_clients, 50, 100),
                threshold_warning=50.0,
                threshold_critical=100.0,
                timestamp=datetime.now(),
                unit="clients",
                description="Number of connected cache clients"
            )
            
            # Update cache component
            cache_status = self.get_worst_status([response_metric, memory_metric, clients_metric])
            self.components["cache"] = ComponentHealth(
                name="cache",
                status=cache_status,
                metrics=[response_metric, memory_metric, clients_metric],
                last_check=datetime.now(),
                uptime=info.get('uptime_in_seconds', 0)
            )
            
            # Store metrics history
            for metric in [response_metric, memory_metric, clients_metric]:
                self.metrics_history[metric.name].append({
                    "timestamp": metric.timestamp,
                    "value": metric.value,
                    "status": metric.status
                })
                
        except Exception as e:
            logger.error(f"Error checking cache health: {str(e)}")
            self.components["cache"] = ComponentHealth(
                name="cache",
                status="unhealthy",
                metrics=[],
                last_check=datetime.now(),
                uptime=0,
                error_count=1,
                last_error=str(e)
            )
    
    async def check_ai_service_health(self):
        """Check AI service connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test OpenAI API connectivity with a simple request
            import openai
            openai.api_key = settings.ai.openai_api_key
            
            # Make a minimal API call
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Create metrics
            response_metric = HealthMetric(
                name="ai_response_time",
                value=response_time,
                status=self.get_status(response_time, 2000, 5000),  # 2s warning, 5s critical
                threshold_warning=2000.0,
                threshold_critical=5000.0,
                timestamp=datetime.now(),
                unit="ms",
                description="AI service response time"
            )
            
            # Check API quota/usage if available
            quota_metric = HealthMetric(
                name="ai_quota_usage",
                value=0,  # This would need to be implemented based on OpenAI's usage API
                status="healthy",
                threshold_warning=80.0,
                threshold_critical=95.0,
                timestamp=datetime.now(),
                unit="%",
                description="AI service quota usage percentage"
            )
            
            # Update AI service component
            ai_status = self.get_worst_status([response_metric, quota_metric])
            self.components["ai_service"] = ComponentHealth(
                name="ai_service",
                status=ai_status,
                metrics=[response_metric, quota_metric],
                last_check=datetime.now(),
                uptime=time.time()  # Assume service uptime
            )
            
            # Store metrics history
            for metric in [response_metric, quota_metric]:
                self.metrics_history[metric.name].append({
                    "timestamp": metric.timestamp,
                    "value": metric.value,
                    "status": metric.status
                })
                
        except Exception as e:
            logger.error(f"Error checking AI service health: {str(e)}")
            self.components["ai_service"] = ComponentHealth(
                name="ai_service",
                status="unhealthy",
                metrics=[],
                last_check=datetime.now(),
                uptime=0,
                error_count=1,
                last_error=str(e)
            )
    
    async def check_storage_health(self):
        """Check storage system health."""
        try:
            import os
            from pathlib import Path
            
            storage_path = Path(settings.storage.local_path)
            
            # Ensure storage directory exists
            storage_path.mkdir(parents=True, exist_ok=True)
            
            # Test write/read operations
            start_time = time.time()
            test_file = storage_path / "health_check.txt"
            
            # Write test
            with open(test_file, 'w') as f:
                f.write("health check test")
            
            # Read test
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Cleanup
            test_file.unlink()
            
            io_time = (time.time() - start_time) * 1000
            
            # Get storage usage
            usage = psutil.disk_usage(str(storage_path))
            free_space_gb = usage.free / (1024 ** 3)
            used_percent = (usage.used / usage.total) * 100
            
            # Count files in storage
            file_count = sum(1 for _ in storage_path.rglob('*') if _.is_file())
            
            # Create metrics
            io_metric = HealthMetric(
                name="storage_io_time",
                value=io_time,
                status=self.get_status(io_time, 100, 500),
                threshold_warning=100.0,
                threshold_critical=500.0,
                timestamp=datetime.now(),
                unit="ms",
                description="Storage I/O operation time"
            )
            
            space_metric = HealthMetric(
                name="storage_free_space",
                value=free_space_gb,
                status=self.get_status(free_space_gb, 5, 1, reverse=True),  # Warning if < 5GB, critical if < 1GB
                threshold_warning=5.0,
                threshold_critical=1.0,
                timestamp=datetime.now(),
                unit="GB",
                description="Available storage space"
            )
            
            files_metric = HealthMetric(
                name="storage_file_count",
                value=file_count,
                status="healthy",  # File count is informational
                threshold_warning=10000.0,
                threshold_critical=50000.0,
                timestamp=datetime.now(),
                unit="files",
                description="Number of files in storage"
            )
            
            # Update storage component
            storage_status = self.get_worst_status([io_metric, space_metric, files_metric])
            self.components["storage"] = ComponentHealth(
                name="storage",
                status=storage_status,
                metrics=[io_metric, space_metric, files_metric],
                last_check=datetime.now(),
                uptime=time.time()
            )
            
            # Store metrics history
            for metric in [io_metric, space_metric, files_metric]:
                self.metrics_history[metric.name].append({
                    "timestamp": metric.timestamp,
                    "value": metric.value,
                    "status": metric.status
                })
                
        except Exception as e:
            logger.error(f"Error checking storage health: {str(e)}")
            self.components["storage"] = ComponentHealth(
                name="storage",
                status="unhealthy",
                metrics=[],
                last_check=datetime.now(),
                uptime=0,
                error_count=1,
                last_error=str(e)
            )
    
    def get_status(self, value: float, warning_threshold: float, critical_threshold: float, reverse: bool = False) -> str:
        """Determine status based on thresholds."""
        if reverse:
            # For metrics where lower values are worse (e.g., free space)
            if value <= critical_threshold:
                return "critical"
            elif value <= warning_threshold:
                return "warning"
            else:
                return "healthy"
        else:
            # For metrics where higher values are worse (e.g., CPU usage)
            if value >= critical_threshold:
                return "critical"
            elif value >= warning_threshold:
                return "warning"
            else:
                return "healthy"
    
    def get_worst_status(self, metrics: List[HealthMetric]) -> str:
        """Get the worst status from a list of metrics."""
        statuses = [metric.status for metric in metrics]
        
        if "critical" in statuses:
            return "unhealthy"
        elif "warning" in statuses:
            return "degraded"
        else:
            return "healthy"
    
    def update_overall_status(self):
        """Update the overall system status based on component health."""
        if not self.components:
            return
        
        component_statuses = [comp.status for comp in self.components.values()]
        
        if "unhealthy" in component_statuses:
            overall_status = "unhealthy"
        elif "degraded" in component_statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Store overall status
        self.overall_status = overall_status
        self.last_health_check = datetime.now()
    
    async def check_alerts(self):
        """Check for conditions that should trigger alerts."""
        current_time = datetime.now()
        
        for component_name, component in self.components.items():
            if component.status in ["degraded", "unhealthy"]:
                # Check if we already have a recent alert for this component
                recent_alert = any(
                    alert["component"] == component_name and 
                    alert["timestamp"] > current_time - timedelta(minutes=15)
                    for alert in self.alerts
                )
                
                if not recent_alert:
                    alert = {
                        "id": f"{component_name}_{int(current_time.timestamp())}",
                        "component": component_name,
                        "status": component.status,
                        "message": f"Component {component_name} is {component.status}",
                        "timestamp": current_time,
                        "metrics": [asdict(metric) for metric in component.metrics if metric.status != "healthy"],
                        "error": component.last_error
                    }
                    
                    self.alerts.append(alert)
                    logger.warning(f"Health alert: {alert['message']}")
                    
                    # Send notification if configured
                    await self.send_alert_notification(alert)
    
    async def send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification via configured channels."""
        try:
            if settings.notifications.enabled:
                # Email notification
                if settings.notifications.email_enabled:
                    await self.send_email_alert(alert)
                
                # Webhook notification
                if settings.notifications.webhook_enabled:
                    await self.send_webhook_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error sending alert notification: {str(e)}")
    
    async def send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert notification."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if not all([settings.notifications.smtp_server, 
                       settings.notifications.smtp_username, 
                       settings.notifications.smtp_password]):
                logger.warning("Email notifications enabled but SMTP settings incomplete")
                return
            
            msg = MIMEMultipart()
            msg['From'] = settings.notifications.smtp_username
            msg['To'] = settings.notifications.smtp_username  # Send to self for now
            msg['Subject'] = f"Health Alert: {alert['component']} is {alert['status']}"
            
            body = f"""
            Health Alert Details:
            
            Component: {alert['component']}
            Status: {alert['status']}
            Message: {alert['message']}
            Timestamp: {alert['timestamp']}
            
            Affected Metrics:
            """
            
            for metric in alert['metrics']:
                body += f"- {metric['name']}: {metric['value']} {metric['unit']} ({metric['status']})\n"
            
            if alert['error']:
                body += f"\nError Details: {alert['error']}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(settings.notifications.smtp_server, settings.notifications.smtp_port)
            server.starttls()
            server.login(settings.notifications.smtp_username, settings.notifications.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert['component']}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
    
    async def send_webhook_alert(self, alert: Dict[str, Any]):
        """Send webhook alert notification."""
        try:
            import aiohttp
            
            if not settings.notifications.webhook_url:
                logger.warning("Webhook notifications enabled but URL not configured")
                return
            
            payload = {
                "type": "health_alert",
                "alert": alert,
                "system": {
                    "app_name": settings.app_name,
                    "environment": settings.environment,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.notifications.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook alert sent for {alert['component']}")
                    else:
                        logger.warning(f"Webhook alert failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending webhook alert: {str(e)}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of current system health."""
        return {
            "overall_status": getattr(self, 'overall_status', 'unknown'),
            "last_check": getattr(self, 'last_health_check', None),
            "components": {
                name: {
                    "status": comp.status,
                    "last_check": comp.last_check,
                    "uptime": comp.uptime,
                    "error_count": comp.error_count,
                    "metrics_count": len(comp.metrics)
                }
                for name, comp in self.components.items()
            },
            "active_alerts": len([a for a in self.alerts if a["timestamp"] > datetime.now() - timedelta(hours=1)]),
            "monitoring_active": self.monitoring_active
        }
    
    def get_component_details(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific component."""
        if component_name not in self.components:
            return None
        
        component = self.components[component_name]
        return {
            "name": component.name,
            "status": component.status,
            "last_check": component.last_check,
            "uptime": component.uptime,
            "error_count": component.error_count,
            "last_error": component.last_error,
            "metrics": [asdict(metric) for metric in component.metrics],
            "history": list(self.metrics_history.get(f"{component_name}_metrics", []))
        }
    
    def get_metrics_history(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric."""
        if metric_name not in self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            entry for entry in self.metrics_history[metric_name]
            if entry["timestamp"] > cutoff_time
        ]
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within the specified time window."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alerts
            if alert["timestamp"] > cutoff_time
        ]
    
    def clear_old_data(self, days: int = 7):
        """Clear old metrics and alerts data."""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Clear old alerts
        self.alerts = [
            alert for alert in self.alerts
            if alert["timestamp"] > cutoff_time
        ]
        
        # Clear old metrics history
        for metric_name, history in self.metrics_history.items():
            while history and history[0]["timestamp"] < cutoff_time:
                history.popleft()
        
        logger.info(f"Cleared health monitoring data older than {days} days")

# Global health monitor instance
health_monitor = HealthMonitor()

# Startup and shutdown functions
async def start_health_monitoring():
    """Start health monitoring on application startup."""
    if settings.monitoring.metrics_enabled:
        asyncio.create_task(health_monitor.start_monitoring())
        logger.info("Health monitoring started")

async def stop_health_monitoring():
    """Stop health monitoring on application shutdown."""
    health_monitor.stop_monitoring()
    logger.info("Health monitoring stopped")