import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from modules.ai_agency.direction_board import direction_board

logger = logging.getLogger(__name__)

router = APIRouter()


class LookerActionPayload(BaseModel):
    workflow_id: str = Field(..., description="Workflow identifier from Looker Action.")
    trigger_source: str = Field("Looker_Action", description="Action trigger source.")
    conditions_met: Dict[str, Any] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)


def _require_token(request: Request) -> None:
    token_required = os.getenv("LOOKER_ACTION_TOKEN")
    if not token_required:
        return
    token = request.headers.get("X-Looker-Token") or request.query_params.get("token")
    if not token or token != token_required:
        raise HTTPException(status_code=403, detail="Invalid Looker Action token.")


def _department_for_workflow(workflow_id: str) -> str:
    workflow = workflow_id.lower()
    if "sales" in workflow:
        return "sales"
    if "support" in workflow or "churn" in workflow:
        return "support"
    return "operations"


def _queue_payload(payload: LookerActionPayload) -> None:
    queue_path = Path("logs") / "looker_actions_queue.jsonl"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write(payload.model_dump_json())
        handle.write("\n")


@router.post("/trigger")
async def looker_trigger(payload: LookerActionPayload, request: Request):
    """
    Public webhook for Looker Actions. Use for orchestration triggers.
    """
    _require_token(request)

    mode = os.getenv("LOOKER_ACTION_MODE", "execute").lower()
    if mode in {"queue", "log-only"}:
        _queue_payload(payload)
        logger.info("Looker trigger queued: %s", payload.workflow_id)
        return {
            "status": "queued",
            "workflow_id": payload.workflow_id,
            "mode": mode,
        }

    department = _department_for_workflow(payload.workflow_id)
    objective_payload = {
        "workflow_id": payload.workflow_id,
        "conditions_met": payload.conditions_met,
        "payload": payload.payload,
        "trigger_source": payload.trigger_source,
    }
    objective = (
        f"Looker Action trigger {payload.workflow_id}. "
        f"Payload: {json.dumps(objective_payload, ensure_ascii=True)}"
    )

    logger.info("Looker trigger received: %s", payload.workflow_id)
    try:
        result = await direction_board.execute_workflow(objective, department)
    except Exception as exc:
        logger.error("Looker trigger failed: %s", exc)
        _queue_payload(payload)
        return {
            "status": "queued",
            "workflow_id": payload.workflow_id,
            "department": department,
            "error": str(exc),
        }

    return {
        "status": "accepted",
        "workflow_id": payload.workflow_id,
        "department": department,
        "result": result,
    }
