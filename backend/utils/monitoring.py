"""
Production Monitoring and Health Checks
System monitoring, performance tracking, and alerting
"""

import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import text
from backend.core.database import get_db

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor system resources and application health."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "uptime": str(datetime.utcnow() - self.start_time),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    async def get_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            async for db in get_db():
                # Test connection
                start_time = datetime.utcnow()
                result = await db.execute(text("SELECT 1"))
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Get database size (SQLite specific)
                try:
                    size_result = await db.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"))
                    db_size = size_result.scalar()
                except:
                    db_size = 0
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "database_size_bytes": db_size,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics."""
        return {
            "uptime": str(datetime.utcnow() - self.start_time),
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.utcnow().isoformat(),
            "process_id": psutil.Process().pid,
            "memory_usage_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": psutil.Process().cpu_percent(),
            "open_files": len(psutil.Process().open_files()),
            "threads": psutil.Process().num_threads()
        }

# Global monitor instance
system_monitor = SystemMonitor()