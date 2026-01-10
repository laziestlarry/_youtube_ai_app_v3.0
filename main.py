import os
import uuid
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any

# -------------------------------------------------
# App + Logging
# -------------------------------------------------

app = FastAPI(title="Propulse AutonomaX Receiver")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autonomax")

# -------------------------------------------------
# Environment
# -------------------------------------------------

BIGQUERY_ENABLED = os.environ.get("BIGQUERY_AUDIT_ENABLED", "true").lower() in {"1", "true", "yes"}

BIGQUERY_PROJECT = os.environ.get("BIGQUERY_PROJECT", "propulse-autonomax")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "profit_os")
BIGQUERY_TABLE   = os.environ.get("BIGQUERY_AUDIT_TABLE", "workflow_events")

# -------------------------------------------------
# Models (matches api_trigger.json exactly)
# -------------------------------------------------

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


# -------------------------------------------------
# Utilities
# -------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def audit_to_bigquery(event: Dict[str, Any]) -> None:
    """
    Writes one audit row to BigQuery.
    Non-fatal by design (never breaks workflow execution).
    """
    if not BIGQUERY_ENABLED:
        return

    try:
        from google.cloud import bigquery

        table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
        client = bigquery.Client(project=BIGQUERY_PROJECT)

        errors = client.insert_rows_json(table_id, [event])
        if errors:
            logger.error(f"❌ BigQuery insert errors: {errors}")
        else:
            logger.info(f"🧾 BigQuery audit inserted: {event['workflow_event_id']}")

    except Exception as e:
        logger.exception(f"❌ BigQuery audit failed (non-fatal): {e}")


# -------------------------------------------------
# Business Logic (unchanged behavior)
# -------------------------------------------------

def execute_churn_prevention(payload: WorkflowPayload):
    logger.info(f"⚡ ACTION STARTED: Assigning Success Manager for {payload.customer_id}")
    logger.info(f"   Reason: {payload.reason_code}")
    import time
    time.sleep(1)
    logger.info(f"✅ ACTION COMPLETED: Workflow for {payload.customer_id} finalized.")


# -------------------------------------------------
# Endpoints
# -------------------------------------------------

@app.get("/")
def health_check():
    return {"status": "operational", "system": "Propulse AutonomaX"}


@app.post("/autonomax/workflows/trigger")
async def trigger_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    logger.info(f"📥 Signal Received: Workflow {request.workflow_id} from {request.trigger_source}")

    workflow_event_id = str(uuid.uuid4())

    # --- Churn Prevention Workflow ---
    if request.workflow_id == "churn_prevention_001":

        if request.conditions_met.predicted_churn == 1:
            # Run business logic async
            background_tasks.add_task(execute_churn_prevention, request.payload)

            # Audit immediately (ACCEPTED)
            audit_to_bigquery({
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
            })

            return {
                "status": "accepted",
                "message": "Churn prevention workflow initiated.",
                "workflow_event_id": workflow_event_id,
            }

        else:
            return {"status": "ignored", "message": "Churn conditions not met."}

    # --- Unknown Workflow ---
    logger.warning(f"Unknown workflow ID: {request.workflow_id}")
    raise HTTPException(status_code=404, detail="Workflow ID not found")


# -------------------------------------------------
# Local / Cloud Run Entry
# -------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
