"""
Base Director - Foundation for all specialized directors
Each director reports to Commander with KPI accountability
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum


class KPIStatus(Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BEHIND = "behind"
    EXCEEDED = "exceeded"


@dataclass
class KPIMetric:
    """Individual KPI with target and tracking"""
    name: str
    target: float
    current: float = 0.0
    unit: str = ""
    period: str = "monthly"  # daily, weekly, monthly, quarterly
    
    @property
    def progress(self) -> float:
        if self.target == 0:
            return 0.0
        return (self.current / self.target) * 100
    
    @property
    def status(self) -> KPIStatus:
        progress = self.progress
        if progress >= 100:
            return KPIStatus.EXCEEDED
        elif progress >= 75:
            return KPIStatus.ON_TRACK
        elif progress >= 50:
            return KPIStatus.AT_RISK
        return KPIStatus.BEHIND
    
    @property
    def gap(self) -> float:
        return self.target - self.current


@dataclass
class DirectorKPIs:
    """KPI container for a director"""
    metrics: Dict[str, KPIMetric] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_metric(self, name: str, target: float, unit: str = "", period: str = "monthly"):
        self.metrics[name] = KPIMetric(name=name, target=target, unit=unit, period=period)
    
    def update_metric(self, name: str, value: float):
        if name in self.metrics:
            self.metrics[name].current = value
            self.last_updated = datetime.utcnow()
    
    def increment_metric(self, name: str, delta: float):
        if name in self.metrics:
            self.metrics[name].current += delta
            self.last_updated = datetime.utcnow()
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            name: {
                "target": m.target,
                "current": m.current,
                "progress": f"{m.progress:.1f}%",
                "status": m.status.value,
                "gap": m.gap,
                "unit": m.unit,
            }
            for name, m in self.metrics.items()
        }
    
    def get_at_risk(self) -> List[str]:
        return [
            name for name, m in self.metrics.items()
            if m.status in [KPIStatus.AT_RISK, KPIStatus.BEHIND]
        ]


@dataclass
class DirectorTask:
    """Task assigned to a director"""
    id: str
    title: str
    description: str
    priority: int  # 1 (highest) to 5 (lowest)
    kpi_impact: List[str]  # Which KPIs this task affects
    due_date: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, blocked
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


class BaseDirector(ABC):
    """
    Abstract base class for all AI Directors.
    
    Directors are specialized agents that own a domain and are accountable
    for specific KPIs. They receive tasks from Commander and execute
    autonomously within their domain.
    """
    
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.kpis = DirectorKPIs()
        self.tasks: List[DirectorTask] = []
        self.execution_log: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"director.{domain}")
        self._initialize_kpis()
    
    @abstractmethod
    def _initialize_kpis(self):
        """Initialize domain-specific KPIs"""
        pass
    
    @abstractmethod
    def execute_task(self, task: DirectorTask) -> Dict[str, Any]:
        """Execute a specific task within domain"""
        pass
    
    @abstractmethod
    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """Get prioritized actions to improve KPIs"""
        pass
    
    def receive_task(self, title: str, description: str, priority: int = 3,
                     kpi_impact: List[str] = None, due_date: datetime = None) -> DirectorTask:
        """Receive a task from Commander"""
        task = DirectorTask(
            id=f"TASK_{self.domain.upper()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=title,
            description=description,
            priority=priority,
            kpi_impact=kpi_impact or [],
            due_date=due_date,
        )
        self.tasks.append(task)
        self.logger.info(f"Received task: {task.id} - {task.title}")
        return task
    
    def process_pending_tasks(self) -> List[Dict[str, Any]]:
        """Process all pending tasks by priority"""
        pending = [t for t in self.tasks if t.status == "pending"]
        pending.sort(key=lambda t: t.priority)
        
        results = []
        for task in pending:
            task.status = "in_progress"
            try:
                result = self.execute_task(task)
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                task.result = result
                results.append({"task_id": task.id, "status": "completed", "result": result})
            except Exception as e:
                task.status = "blocked"
                task.result = {"error": str(e)}
                results.append({"task_id": task.id, "status": "blocked", "error": str(e)})
                self.logger.error(f"Task {task.id} blocked: {e}")
        
        return results
    
    def report_to_commander(self) -> Dict[str, Any]:
        """Generate status report for Commander"""
        completed = [t for t in self.tasks if t.status == "completed"]
        in_progress = [t for t in self.tasks if t.status == "in_progress"]
        blocked = [t for t in self.tasks if t.status == "blocked"]
        pending = [t for t in self.tasks if t.status == "pending"]
        
        return {
            "director": self.name,
            "domain": self.domain,
            "kpis": self.kpis.get_summary(),
            "at_risk_kpis": self.kpis.get_at_risk(),
            "tasks": {
                "completed": len(completed),
                "in_progress": len(in_progress),
                "blocked": len(blocked),
                "pending": len(pending),
            },
            "priority_actions": self.get_priority_actions()[:5],
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def log_execution(self, action: str, result: Dict[str, Any]):
        """Log execution for audit trail"""
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "result": result,
        })
