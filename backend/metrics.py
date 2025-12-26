from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import time
import functools
from typing import Callable, Any
import asyncio

# Create custom registry
registry = CollectorRegistry()

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

video_processing_duration_seconds = Histogram(
    'video_processing_duration_seconds',
    'Video processing duration in seconds',
    ['stage'],
    registry=registry
)

active_video_generations = Gauge(
    'active_video_generations',
    'Number of active video generations',
    registry=registry
)

database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections',
    registry=registry
)

redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status'],
    registry=registry
)

ai_api_calls_total = Counter(
    'ai_api_calls_total',
    'Total AI API calls',
    ['provider', 'model', 'status'],
    registry=registry
)

revenue_generated_total = Counter(
    'revenue_generated_total',
    'Total revenue generated',
    ['source'],
    registry=registry
)

video_upload_success_total = Counter(
    'video_upload_success_total',
    'Total successful video uploads',
    registry=registry
)

video_upload_failure_total = Counter(
    'video_upload_failure_total',
    'Total failed video uploads',
    ['reason'],
    registry=registry
)

def track_time(metric: Histogram, labels: dict = None):
    """Decorator to track execution time."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def track_counter(metric: Counter, labels: dict = None):
    """Decorator to track counter metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                result = await func(*args, **kwargs)
                if labels:
                    metric.labels(**labels).inc()
                else:
                    metric.inc()
                return result
            except Exception as e:
                if labels:
                    error_labels = {**labels, 'status': 'error'}
                    metric.labels(**error_labels).inc()
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                if labels:
                    metric.labels(**labels).inc()
                else:
                    metric.inc()
                return result
            except Exception as e:
                if labels:
                    error_labels = {**labels, 'status': 'error'}
                    metric.labels(**error_labels).inc()
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class MetricsCollector:
    """Centralized metrics collection."""
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def record_video_processing(stage: str, duration: float):
        """Record video processing metrics."""
        video_processing_duration_seconds.labels(stage=stage).observe(duration)
    
    @staticmethod
    def set_active_generations(count: int):
        """Set number of active video generations."""
        active_video_generations.set(count)
    
    @staticmethod
    def record_ai_api_call(provider: str, model: str, success: bool):
        """Record AI API call metrics."""
        status = 'success' if success else 'error'
        ai_api_calls_total.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
    
    @staticmethod
    def record_revenue(source: str, amount: float):
        """Record revenue metrics."""
        revenue_generated_total.labels(source=source).inc(amount)
    
    @staticmethod
    def record_video_upload(success: bool, reason: str = None):
        """Record video upload metrics."""
        if success:
            video_upload_success_total.inc()
        else:
            video_upload_failure_total.labels(reason=reason or 'unknown').inc()
    
    @staticmethod
    def record_redis_operation(operation: str, success: bool):
        """Record Redis operation metrics."""
        status = 'success' if success else 'error'
        redis_operations_total.labels(
            operation=operation,
            status=status
        ).inc()