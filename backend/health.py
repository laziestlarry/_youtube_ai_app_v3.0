from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
import time
from datetime import datetime
import psutil
import redis
import asyncpg
from sqlalchemy import text

from .database_manager import DatabaseManager
from .config import get_settings

settings = get_settings()
health_router = APIRouter()

class HealthChecker:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.start_time = time.time()
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            async with self.db_manager.get_connection() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()
            
            response_time = (time.time() - start_time) * 1000
            
            # Check database stats
            async with self.db_manager.get_connection() as conn:
                stats_query = text("""
                    SELECT 
                        (SELECT count(*) FROM videos) as video_count,
                        (SELECT count(*) FROM content_ideas) as ideas_count,
                        (SELECT count(*) FROM monetization) as monetization_records
                """)
                result = await conn.execute(stats_query)
                stats = await result.fetchone()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "stats": {
                    "videos": stats[0] if stats else 0,
                    "ideas": stats[1] if stats else 0,
                    "monetization_records": stats[2] if stats else 0
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        try:
            start_time = time.time()
            
            r = redis.from_url(settings.redis_url)
            
            # Test basic operations
            test_key = f"health_check_{int(time.time())}"
            r.set(test_key, "test_value", ex=60)
            value = r.get(test_key)
            r.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = r.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "stats": {
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed")
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity."""
        checks = {}
        
        # YouTube API check
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={
                        "part": "id",
                        "mine": "true",
                        "key": settings.youtube_api_key
                    },
                    timeout=10.0
                )
                checks["youtube_api"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_code": response.status_code
                }
        except Exception as e:
            checks["youtube_api"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # OpenAI API check
        try:
            import openai
            openai.api_key = settings.openai_api_key
            
            start_time = time.time()
            response = await openai.Model.alist()
            response_time = (time.time() - start_time) * 1000
            
            checks["openai_api"] = {
                "status": "healthy",
                "response_time_ms": round(response_time, 2)
            }
        except Exception as e:
            checks["openai_api"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return checks
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get application uptime."""
        uptime_seconds = time.time() - self.start_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        return {
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_formatted": f"{days}d {hours}h {minutes}m {seconds}s",
            "started_at": datetime.fromtimestamp(self.start_time).isoformat()
        }

health_checker = HealthChecker()

@health_router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "youtube-ai-app"
    }

@health_router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all components."""
    try:
        # Run all health checks concurrently
        database_check, redis_check, external_apis_check = await asyncio.gather(
            health_checker.check_database(),
            health_checker.check_redis(),
            health_checker.check_external_apis(),
            return_exceptions=True
        )
        
        system_check = health_checker.check_system_resources()
        uptime_info = health_checker.get_uptime()
        
        # Determine overall health
        components = [database_check, redis_check, system_check]
        overall_status = "healthy"
        
        for component in components:
            if isinstance(component, Exception):
                overall_status = "unhealthy"
                break
            elif isinstance(component, dict) and component.get("status") == "unhealthy":
                overall_status = "unhealthy"
                break
        
        # Check if any external API is down (warning, not critical)
        external_api_issues = []
        if isinstance(external_apis_check, dict):
            for api_name, api_status in external_apis_check.items():
                if api_status.get("status") == "unhealthy":
                    external_api_issues.append(api_name)
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": uptime_info,
            "components": {
                "database": database_check if not isinstance(database_check, Exception) else {"status": "unhealthy", "error": str(database_check)},
                "redis": redis_check if not isinstance(redis_check, Exception) else {"status": "unhealthy", "error": str(redis_check)},
                "system": system_check,
                "external_apis": external_apis_check if not isinstance(external_apis_check, Exception) else {"error": str(external_apis_check)}
            },
            "warnings": external_api_issues if external_api_issues else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@health_router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    try:
        # Check critical components only
        db_check = await health_checker.check_database()
        redis_check = await health_checker.check_redis()
        
        if db_check.get("status") == "healthy" and redis_check.get("status") == "healthy":
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Readiness check failed: {str(e)}"
        )

@health_router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@health_router.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from .metrics import registry
        
        return Response(
            generate_latest(registry),
            media_type=CONTENT_TYPE_LATEST
        )
    except ImportError:
        return {"error": "Prometheus client not installed"}