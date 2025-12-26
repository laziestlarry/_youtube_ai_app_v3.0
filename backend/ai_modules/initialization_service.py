from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta
import asyncio
from .management_engine import ManagementEngine
from .content_strategy import ContentStrategyOptimizer
from .analytics_engine import AnalyticsEngine
from .content_optimizer import ContentOptimizer
from .content_enhancer import ContentEnhancer
from .progress_reporter import ProgressReporter, SystemProgress, WorkflowProgress, TaskProgress
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)
router = APIRouter()

class InitializationStatus(BaseModel):
    status: str
    progress: float
    current_task: str
    errors: List[str] = []

class InitializationResponse(BaseModel):
    status: str
    message: str

class InitializationService:
    def __init__(self):
        self.progress_reporter = ProgressReporter()
        self.management_engine = ManagementEngine()
        self.strategy_optimizer = ContentStrategyOptimizer()
        self.analytics_engine = AnalyticsEngine()
        self.content_optimizer = ContentOptimizer()
        self.content_enhancer = ContentEnhancer()
        self.system_id = "youtube_ai_system"
        self.initialization_in_progress = False

    async def initialize_system(self) -> InitializationResponse:
        """Initialize the entire system with progress tracking."""
        if self.initialization_in_progress:
            raise HTTPException(status_code=400, detail="Initialization already in progress")

        try:
            self.initialization_in_progress = True
            system_progress = self.progress_reporter.start_system_initialization(self.system_id)
            self.progress_reporter.update_system_progress(self.system_id, 0.0, "initializing")

            # Initialize analytics
            analytics_workflow = self.progress_reporter.start_workflow(
                "analytics_init",
                "Analytics Initialization"
            )
            await self._initialize_analytics(analytics_workflow.workflow_id)
            self.progress_reporter.complete_workflow(analytics_workflow.workflow_id)
            self.progress_reporter.update_system_progress(self.system_id, 25.0)

            # Initialize content strategy
            strategy_workflow = self.progress_reporter.start_workflow(
                "strategy_init",
                "Strategy Initialization"
            )
            await self._initialize_strategy(strategy_workflow.workflow_id)
            self.progress_reporter.complete_workflow(strategy_workflow.workflow_id)
            self.progress_reporter.update_system_progress(self.system_id, 50.0)

            # Initialize content optimization
            optimization_workflow = self.progress_reporter.start_workflow(
                "optimization_init",
                "Optimization Initialization"
            )
            await self._initialize_optimization(optimization_workflow.workflow_id)
            self.progress_reporter.complete_workflow(optimization_workflow.workflow_id)
            self.progress_reporter.update_system_progress(self.system_id, 75.0)

            # Initialize content enhancement
            enhancement_workflow = self.progress_reporter.start_workflow(
                "enhancement_init",
                "Enhancement Initialization"
            )
            await self._initialize_enhancement(enhancement_workflow.workflow_id)
            self.progress_reporter.complete_workflow(enhancement_workflow.workflow_id)
            self.progress_reporter.update_system_progress(self.system_id, 100.0)

            # Complete system initialization
            self.progress_reporter.complete_system_initialization(self.system_id)
            self.initialization_in_progress = False

            return InitializationResponse(
                status="initialization_started",
                message="System initialization started successfully"
            )

        except Exception as e:
            self.initialization_in_progress = False
            logger.error(f"Initialization failed: {str(e)}")
            self.progress_reporter.update_system_progress(
                self.system_id,
                progress=0.0,
                status="error",
                errors=[str(e)]
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def _initialize_analytics(self, workflow_id: str):
        """Initialize analytics with progress tracking."""
        try:
            # Configure analytics tracking
            task = self.progress_reporter.start_task(
                "analytics_config",
                "Configure Analytics",
                workflow_id
            )
            await self.analytics_engine.configure_tracking({
                "tracking_frequency": "hourly",
                "metrics": ["views", "engagement", "revenue", "growth"],
                "alerts": {
                    "threshold": 0.8,
                    "notifications": ["email", "dashboard"]
                }
            })
            self.progress_reporter.complete_task(task.task_id)

            # Set up performance monitoring
            task = self.progress_reporter.start_task(
                "performance_monitoring",
                "Set Up Performance Monitoring",
                workflow_id
            )
            await self.analytics_engine.setup_performance_monitoring()
            self.progress_reporter.complete_task(task.task_id)

        except Exception as e:
            self.progress_reporter.update_workflow_progress(
                workflow_id,
                progress=0.0,
                status="error",
                errors=[str(e)]
            )
            raise

    async def _initialize_strategy(self, workflow_id: str):
        """Initialize content strategy with progress tracking."""
        try:
            # Configure content strategy
            task = self.progress_reporter.start_task(
                "strategy_config",
                "Configure Content Strategy",
                workflow_id
            )
            await self.strategy_optimizer.configure_strategy({
                "posting_frequency": "daily",
                "content_types": ["tutorial", "entertainment", "educational"],
                "optimization_targets": ["engagement", "views", "revenue"]
            })
            self.progress_reporter.complete_task(task.task_id)

            # Set up content calendar
            task = self.progress_reporter.start_task(
                "calendar_setup",
                "Set Up Content Calendar",
                workflow_id
            )
            await self.strategy_optimizer.setup_content_calendar()
            self.progress_reporter.complete_task(task.task_id)

        except Exception as e:
            self.progress_reporter.update_workflow_progress(
                workflow_id,
                progress=0.0,
                status="error",
                errors=[str(e)]
            )
            raise

    async def _initialize_optimization(self, workflow_id: str):
        """Initialize content optimization with progress tracking."""
        try:
            # Configure optimization settings
            task = self.progress_reporter.start_task(
                "optimization_config",
                "Configure Optimization Settings",
                workflow_id
            )
            await self.content_optimizer.configure_optimization({
                "optimization_frequency": "daily",
                "target_metrics": ["views", "engagement", "revenue"],
                "optimization_methods": ["metadata", "content", "timing"]
            })
            self.progress_reporter.complete_task(task.task_id)

            # Set up optimization workflows
            task = self.progress_reporter.start_task(
                "workflow_setup",
                "Set Up Optimization Workflows",
                workflow_id
            )
            await self.content_optimizer.setup_optimization_workflows()
            self.progress_reporter.complete_task(task.task_id)

        except Exception as e:
            self.progress_reporter.update_workflow_progress(
                workflow_id,
                progress=0.0,
                status="error",
                errors=[str(e)]
            )
            raise

    async def _initialize_enhancement(self, workflow_id: str):
        """Initialize content enhancement with progress tracking."""
        try:
            # Configure enhancement settings
            task = self.progress_reporter.start_task(
                "enhancement_config",
                "Configure Enhancement Settings",
                workflow_id
            )
            await self.content_enhancer.configure_enhancement({
                "enhancement_frequency": "on-demand",
                "enhancement_types": ["title", "description", "thumbnail", "tags"],
                "quality_threshold": 0.8
            })
            self.progress_reporter.complete_task(task.task_id)

            # Set up enhancement workflows
            task = self.progress_reporter.start_task(
                "enhancement_workflow",
                "Set Up Enhancement Workflows",
                workflow_id
            )
            await self.content_enhancer.setup_enhancement_workflows()
            self.progress_reporter.complete_task(task.task_id)

        except Exception as e:
            self.progress_reporter.update_workflow_progress(
                workflow_id,
                progress=0.0,
                status="error",
                errors=[str(e)]
            )
            raise

    def get_initialization_status(self) -> InitializationStatus:
        """Get the current initialization status."""
        system_progress = self.progress_reporter.get_system_progress(self.system_id)
        
        if not system_progress:
            return InitializationStatus(
                status="not_started",
                progress=0.0,
                current_task="",
                errors=[]
            )

        current_task = ""
        if system_progress.workflows:
            latest_workflow = system_progress.workflows[-1]
            if latest_workflow.tasks:
                current_task = latest_workflow.tasks[-1].name

        return InitializationStatus(
            status=system_progress.status,
            progress=system_progress.progress,
            current_task=current_task,
            errors=system_progress.errors
        )

def get_initialization_service():
    return InitializationService()

@router.post("/initialize", response_model=InitializationResponse)
async def initialize_system(service: InitializationService = Depends(get_initialization_service)):
    logger.info("Initialization endpoint called")
    return {"status": "initialization_called", "message": "Initialization endpoint was called"}

@router.get("/status", response_model=InitializationStatus)
async def get_status(service: InitializationService = Depends(get_initialization_service)):
    logger.info("Status endpoint called")
    try:
        status = service.get_initialization_status()
        # Ensure status is 'idle' if not started
        if status.status == 'not_started':
            status.status = 'idle'
        # Convert to JSON-serializable dict
        return jsonable_encoder(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return InitializationStatus(
            status="error",
            progress=0.0,
            current_task="",
            errors=[str(e)]
        )