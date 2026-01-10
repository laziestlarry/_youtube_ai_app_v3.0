from typing import Dict
from .base import BaseWorkflow
from .churn_prevention_001 import ChurnPrevention001Workflow
from .market_dominance_001 import MarketDominance001Workflow

WORKFLOW_REGISTRY: Dict[str, BaseWorkflow] = {
    ChurnPrevention001Workflow.id: ChurnPrevention001Workflow(),
    MarketDominance001Workflow.id: MarketDominance001Workflow(),
}

def get_workflow(workflow_id: str) -> BaseWorkflow | None:
    return WORKFLOW_REGISTRY.get(workflow_id)

def list_workflows() -> list[str]:
    return sorted(WORKFLOW_REGISTRY.keys())
