from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pydantic import BaseModel

class TaskProgress(BaseModel):
    task_id: str
    name: str
    status: str
    progress: float
    start_time: datetime
    end_time: Optional[datetime] = None
    details: Dict[str, Any] = {}
    errors: List[str] = []

class WorkflowProgress(BaseModel):
    workflow_id: str
    name: str
    status: str
    progress: float
    start_time: datetime
    end_time: Optional[datetime] = None
    tasks: List[TaskProgress] = []
    metrics: Dict[str, Any] = {}
    errors: List[str] = []

class SystemProgress(BaseModel):
    system_id: str
    status: str
    progress: float
    start_time: datetime
    end_time: Optional[datetime] = None
    workflows: List[WorkflowProgress] = []
    system_metrics: Dict[str, Any] = {}
    errors: List[str] = []

class ProgressReporter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system_progress: Dict[str, SystemProgress] = {}
        self.workflow_progress: Dict[str, WorkflowProgress] = {}
        self.task_progress: Dict[str, TaskProgress] = {}

    def start_system_initialization(self, system_id: str) -> SystemProgress:
        """Start tracking system initialization progress."""
        progress = SystemProgress(
            system_id=system_id,
            status="initializing",
            progress=0.0,
            start_time=datetime.now(),
            workflows=[],
            system_metrics={},
            errors=[]
        )
        self.system_progress[system_id] = progress
        self.logger.info(f"Started system initialization: {system_id}")
        return progress

    def update_system_progress(self, system_id: str, progress: float, status: str = None, 
                             metrics: Dict[str, Any] = None, errors: List[str] = None) -> SystemProgress:
        """Update system initialization progress."""
        if system_id not in self.system_progress:
            raise ValueError(f"System {system_id} not found")
        
        system = self.system_progress[system_id]
        system.progress = progress
        if status:
            system.status = status
        if metrics:
            system.system_metrics.update(metrics)
        if errors:
            system.errors.extend(errors)
        
        self.logger.info(f"Updated system progress: {system_id} - {progress}%")
        return system

    def complete_system_initialization(self, system_id: str) -> SystemProgress:
        """Mark system initialization as complete."""
        if system_id not in self.system_progress:
            raise ValueError(f"System {system_id} not found")
        
        system = self.system_progress[system_id]
        system.status = "completed"
        system.progress = 100.0
        system.end_time = datetime.now()
        
        self.logger.info(f"Completed system initialization: {system_id}")
        return system

    def start_workflow(self, workflow_id: str, name: str) -> WorkflowProgress:
        """Start tracking workflow progress."""
        progress = WorkflowProgress(
            workflow_id=workflow_id,
            name=name,
            status="running",
            progress=0.0,
            start_time=datetime.now(),
            tasks=[],
            metrics={},
            errors=[]
        )
        self.workflow_progress[workflow_id] = progress
        self.logger.info(f"Started workflow: {workflow_id} - {name}")
        return progress

    def update_workflow_progress(self, workflow_id: str, progress: float, status: str = None,
                               metrics: Dict[str, Any] = None, errors: List[str] = None) -> WorkflowProgress:
        """Update workflow progress."""
        if workflow_id not in self.workflow_progress:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_progress[workflow_id]
        workflow.progress = progress
        if status:
            workflow.status = status
        if metrics:
            workflow.metrics.update(metrics)
        if errors:
            workflow.errors.extend(errors)
        
        self.logger.info(f"Updated workflow progress: {workflow_id} - {progress}%")
        return workflow

    def complete_workflow(self, workflow_id: str) -> WorkflowProgress:
        """Mark workflow as complete."""
        if workflow_id not in self.workflow_progress:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_progress[workflow_id]
        workflow.status = "completed"
        workflow.progress = 100.0
        workflow.end_time = datetime.now()
        
        self.logger.info(f"Completed workflow: {workflow_id}")
        return workflow

    def start_task(self, task_id: str, name: str, workflow_id: str) -> TaskProgress:
        """Start tracking task progress."""
        progress = TaskProgress(
            task_id=task_id,
            name=name,
            status="running",
            progress=0.0,
            start_time=datetime.now(),
            details={},
            errors=[]
        )
        self.task_progress[task_id] = progress
        
        if workflow_id in self.workflow_progress:
            self.workflow_progress[workflow_id].tasks.append(progress)
        
        self.logger.info(f"Started task: {task_id} - {name}")
        return progress

    def update_task_progress(self, task_id: str, progress: float, status: str = None,
                           details: Dict[str, Any] = None, errors: List[str] = None) -> TaskProgress:
        """Update task progress."""
        if task_id not in self.task_progress:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.task_progress[task_id]
        task.progress = progress
        if status:
            task.status = status
        if details:
            task.details.update(details)
        if errors:
            task.errors.extend(errors)
        
        self.logger.info(f"Updated task progress: {task_id} - {progress}%")
        return task

    def complete_task(self, task_id: str) -> TaskProgress:
        """Mark task as complete."""
        if task_id not in self.task_progress:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.task_progress[task_id]
        task.status = "completed"
        task.progress = 100.0
        task.end_time = datetime.now()
        
        self.logger.info(f"Completed task: {task_id}")
        return task

    def get_system_progress(self, system_id: str) -> Optional[SystemProgress]:
        """Get system progress by ID."""
        return self.system_progress.get(system_id)

    def get_workflow_progress(self, workflow_id: str) -> Optional[WorkflowProgress]:
        """Get workflow progress by ID."""
        return self.workflow_progress.get(workflow_id)

    def get_task_progress(self, task_id: str) -> Optional[TaskProgress]:
        """Get task progress by ID."""
        return self.task_progress.get(task_id)

    def get_all_system_progress(self) -> List[SystemProgress]:
        """Get all system progress."""
        return list(self.system_progress.values())

    def get_all_workflow_progress(self) -> List[WorkflowProgress]:
        """Get all workflow progress."""
        return list(self.workflow_progress.values())

    def get_all_task_progress(self) -> List[TaskProgress]:
        """Get all task progress."""
        return list(self.task_progress.values())

    def clear_completed_progress(self, max_age_hours: int = 24):
        """Clear completed progress older than max_age_hours."""
        current_time = datetime.now()
        max_age = timedelta(hours=max_age_hours)

        # Clear completed tasks
        self.task_progress = {
            task_id: task for task_id, task in self.task_progress.items()
            if task.status != "completed" or 
            (task.end_time and (current_time - task.end_time) <= max_age)
        }

        # Clear completed workflows
        self.workflow_progress = {
            workflow_id: workflow for workflow_id, workflow in self.workflow_progress.items()
            if workflow.status != "completed" or 
            (workflow.end_time and (current_time - workflow.end_time) <= max_age)
        }

        # Clear completed systems
        self.system_progress = {
            system_id: system for system_id, system in self.system_progress.items()
            if system.status != "completed" or 
            (system.end_time and (current_time - system.end_time) <= max_age)
        }

        self.logger.info(f"Cleared completed progress older than {max_age_hours} hours") 