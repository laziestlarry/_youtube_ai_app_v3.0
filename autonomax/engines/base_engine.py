"""
Base Engine - Foundation for all AutonomaX execution engines
Implements the engine scaffolding pattern from knowledge base
"""

import logging
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path


class EngineStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a unit of work in the job queue"""
    id: str
    job_type: str
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.QUEUED
    priority: int = 5  # 1-10, higher is more urgent
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    owner: Optional[str] = None


@dataclass
class EngineMetrics:
    """Track engine performance and health"""
    jobs_processed: int = 0
    jobs_succeeded: int = 0
    jobs_failed: int = 0
    total_runtime_ms: int = 0
    last_run: Optional[datetime] = None
    revenue_generated: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.jobs_processed == 0:
            return 0.0
        return self.jobs_succeeded / self.jobs_processed * 100


class BaseEngine(ABC):
    """
    Abstract base class for all AutonomaX engines.
    Follows engine scaffolding pattern:
    - Name, Objective, Inputs, Outputs
    - Dependencies, Metrics, Failure modes
    - Upgrade path
    """
    
    def __init__(self, name: str, objective: str):
        self.name = name
        self.objective = objective
        self.status = EngineStatus.IDLE
        self.metrics = EngineMetrics()
        self.job_queue: List[Job] = []
        self.logger = logging.getLogger(f"engine.{name}")
        self.dependencies: List[str] = []
        self.subscribers: List[Callable] = []
        self._initialize()
    
    def _initialize(self):
        """Engine-specific initialization"""
        self.logger.info(f"Initializing {self.name} engine")
    
    @abstractmethod
    def process_job(self, job: Job) -> Dict[str, Any]:
        """Process a single job - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_inputs(self) -> List[str]:
        """Define required inputs for this engine"""
        pass
    
    @abstractmethod
    def get_outputs(self) -> List[str]:
        """Define outputs produced by this engine"""
        pass
    
    def enqueue(self, job_type: str, payload: Dict[str, Any], priority: int = 5) -> Job:
        """Add a job to the queue"""
        job = Job(
            id=f"{self.name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            job_type=job_type,
            payload=payload,
            priority=priority
        )
        self.job_queue.append(job)
        self.job_queue.sort(key=lambda j: (-j.priority, j.created_at))
        self.logger.info(f"Enqueued job {job.id} (type: {job_type}, priority: {priority})")
        return job
    
    def run(self) -> Dict[str, Any]:
        """Execute the engine's job queue"""
        self.status = EngineStatus.RUNNING
        results = []
        
        while self.job_queue:
            job = self.job_queue.pop(0)
            
            if job.status == JobStatus.CANCELLED:
                continue
            
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.attempts += 1
            
            try:
                result = self.process_job(job)
                job.status = JobStatus.SUCCEEDED
                job.result = result
                self.metrics.jobs_succeeded += 1
                results.append({"job_id": job.id, "status": "success", "result": result})
                
            except Exception as e:
                job.error = str(e)
                self.logger.error(f"Job {job.id} failed: {e}")
                
                if job.attempts < job.max_attempts:
                    job.status = JobStatus.QUEUED
                    self.job_queue.append(job)
                    self.logger.info(f"Retrying job {job.id} (attempt {job.attempts}/{job.max_attempts})")
                else:
                    job.status = JobStatus.FAILED
                    self.metrics.jobs_failed += 1
                    results.append({"job_id": job.id, "status": "failed", "error": str(e)})
            
            finally:
                job.finished_at = datetime.utcnow()
                self.metrics.jobs_processed += 1
                if job.started_at:
                    runtime = (job.finished_at - job.started_at).total_seconds() * 1000
                    self.metrics.total_runtime_ms += int(runtime)
        
        self.status = EngineStatus.COMPLETED
        self.metrics.last_run = datetime.utcnow()
        self._notify_subscribers(results)
        
        return {
            "engine": self.name,
            "status": "completed",
            "jobs_processed": len(results),
            "results": results,
            "metrics": {
                "success_rate": self.metrics.success_rate,
                "total_runtime_ms": self.metrics.total_runtime_ms,
            }
        }
    
    def subscribe(self, callback: Callable):
        """Subscribe to engine completion events"""
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, results: List[Dict]):
        """Notify all subscribers of engine completion"""
        for callback in self.subscribers:
            try:
                callback(self.name, results)
            except Exception as e:
                self.logger.error(f"Subscriber notification failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status and metrics"""
        return {
            "name": self.name,
            "objective": self.objective,
            "status": self.status.value,
            "queue_length": len(self.job_queue),
            "metrics": {
                "jobs_processed": self.metrics.jobs_processed,
                "jobs_succeeded": self.metrics.jobs_succeeded,
                "jobs_failed": self.metrics.jobs_failed,
                "success_rate": f"{self.metrics.success_rate:.1f}%",
                "revenue_generated": self.metrics.revenue_generated,
                "last_run": self.metrics.last_run.isoformat() if self.metrics.last_run else None,
            }
        }
    
    def to_json(self) -> str:
        """Serialize engine state to JSON"""
        return json.dumps(self.get_status(), indent=2, default=str)
