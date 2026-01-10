from __future__ import annotations
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from google.cloud import bigquery


def _utc_now():
    return datetime.now(timezone.utc)


class BigQueryAuditLogger:
    def __init__(self):
        self.project = os.environ.get("BIGQUERY_PROJECT", "propulse-autonomax")
        self.dataset = os.environ.get("BIGQUERY_DATASET", "profit_os")
        self.table = os.environ.get("BIGQUERY_AUDIT_TABLE", "workflow_events")
        self.service = os.environ.get("SERVICE_NAME", "execution-pack")

        self.client = bigquery.Client(project=self.project)
        self.table_id = f"{self.project}.{self.dataset}.{self.table}"

    def log_event(
        self,
        *,
        workflow_id: str,
        trigger_source: str,
        status: str,
        customer_id: Optional[str],
        reason_code: Optional[str],
        predicted_churn: Optional[int],
        customer_value: Optional[str],
        request_json: Dict[str, Any],
        result_json: Dict[str, Any],
    ) -> str:
        event_id = str(uuid.uuid4())

        row = {
            "workflow_event_id": event_id,
            "ts": _utc_now().isoformat(),
            "service": self.service,
            "workflow_id": workflow_id,
            "trigger_source": trigger_source,
            "customer_id": customer_id or "",
            "status": status,
            "reason_code": reason_code or "",
            "predicted_churn": int(predicted_churn) if predicted_churn is not None else None,
            "customer_value": customer_value or "",
            "request_json": request_json,
            "result_json": result_json,
        }

        errors = self.client.insert_rows_json(self.table_id, [row])
        if errors:
            # Don’t break production workflows due to audit issues.
            # Raise only if you want “audit required” semantics.
            raise RuntimeError(f"BigQuery insert error(s): {errors}")

        return event_id
