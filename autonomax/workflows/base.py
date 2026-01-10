from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class WorkflowContext:
    workflow_id: str
    trigger_source: str
    conditions_met: Dict[str, Any]
    payload: Dict[str, Any]
    received_at: datetime

    @staticmethod
    def from_trigger(body: Dict[str, Any]) -> "WorkflowContext":
        return WorkflowContext(
            workflow_id=body["workflow_id"],
            trigger_source=body.get("trigger_source", "unknown"),
            conditions_met=body.get("conditions_met", {}),
            payload=body.get("payload", {}),
            received_at=datetime.now(timezone.utc),
        )


class WorkflowResult(Dict[str, Any]):
    pass


class BaseWorkflow:
    """Base class for all workflows."""
    id: str = "base"

    async def execute(self, ctx: WorkflowContext) -> WorkflowResult:
        raise NotImplementedError
