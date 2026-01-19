"""
Root entrypoint for local/dev + CI.

Historically this repo contained multiple FastAPI apps. The backend API used by
the test suite lives in `backend/main.py` and is exposed here as `app` so that
`from main import app` works in all environments.

If you need the lightweight "receiver" service, set `APP_MODE=receiver`.
"""

from __future__ import annotations

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel


def _create_receiver_app() -> FastAPI:
    app = FastAPI(title="Propulse AutonomaX Receiver")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("autonomax")

    bigquery_enabled = os.environ.get("BIGQUERY_AUDIT_ENABLED", "true").lower() in {"1", "true", "yes"}
    bigquery_project = os.environ.get("BIGQUERY_PROJECT", "propulse-autonomax")
    bigquery_dataset = os.environ.get("BIGQUERY_DATASET", "profit_os")
    bigquery_table = os.environ.get("BIGQUERY_AUDIT_TABLE", "workflow_events")

    class TriggerConditions(BaseModel):
        predicted_churn: int
        customer_value: str

    class WorkflowPayload(BaseModel):
        customer_id: str
        reason_code: str
        action: str

    class WorkflowRequest(BaseModel):
        workflow_id: str
        trigger_source: str
        conditions_met: TriggerConditions
        payload: WorkflowPayload

    def utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def audit_to_bigquery(event: Dict[str, Any]) -> None:
        if not bigquery_enabled:
            return
        try:
            from google.cloud import bigquery

            table_id = f"{bigquery_project}.{bigquery_dataset}.{bigquery_table}"
            client = bigquery.Client(project=bigquery_project)
            errors = client.insert_rows_json(table_id, [event])
            if errors:
                logger.error("BigQuery insert errors: %s", errors)
        except Exception as exc:
            logger.exception("BigQuery audit failed (non-fatal): %s", exc)

    def execute_churn_prevention(payload: WorkflowPayload) -> None:
        logger.info("Assigning Success Manager for %s", payload.customer_id)

    @app.get("/")
    def health_check():
        return {"status": "operational", "system": "Propulse AutonomaX Receiver"}

    @app.post("/autonomax/workflows/trigger")
    async def trigger_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
        workflow_event_id = str(uuid.uuid4())

        if request.workflow_id == "churn_prevention_001":
            if request.conditions_met.predicted_churn == 1:
                background_tasks.add_task(execute_churn_prevention, request.payload)
                audit_to_bigquery(
                    {
                        "workflow_event_id": workflow_event_id,
                        "ts": utc_now_iso(),
                        "service": os.environ.get("K_SERVICE", "execution-pack"),
                        "workflow_id": request.workflow_id,
                        "trigger_source": request.trigger_source,
                        "customer_id": request.payload.customer_id,
                        "status": "accepted",
                        "reason_code": request.payload.reason_code,
                        "predicted_churn": request.conditions_met.predicted_churn,
                        "customer_value": request.conditions_met.customer_value,
                        "request_json": request.model_dump(),
                        "result_json": {"status": "accepted", "message": "queued"},
                    }
                )
                return {
                    "status": "accepted",
                    "message": "Churn prevention workflow initiated.",
                    "workflow_event_id": workflow_event_id,
                }
            return {"status": "ignored", "message": "Churn conditions not met."}

        raise HTTPException(status_code=404, detail="Workflow ID not found")

    return app


app_mode = os.environ.get("APP_MODE", "platform").strip().lower()
if app_mode in {"receiver", "execution-pack", "execution_pack"}:
    app = _create_receiver_app()
else:
    from backend.main import app  # noqa: F401


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

