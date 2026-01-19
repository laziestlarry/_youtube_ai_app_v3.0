import json
import os
from datetime import datetime
from typing import Dict, Any, List

from autonomax.app.main import SessionLocal
from autonomax.app.models import Job, WorkItem, JobStatus


def _append_log(entry: Dict[str, Any]) -> None:
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "mission_actions.jsonl")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _execute_action_plan(item: WorkItem, job: Job) -> Dict[str, Any]:
    action_plan = (job.payload_json or {}).get("action_plan", {})
    now = datetime.utcnow().isoformat()
    result = {
        "work_item_id": item.id,
        "job_id": job.id,
        "category": item.category,
        "source_type": item.source_type,
        "source_ref": item.source_ref,
        "executed_at": now,
        "action_plan": action_plan,
        "status": "completed",
    }
    _append_log(result)
    return result


def run_job_queue(limit: int = 5) -> Dict[str, Any]:
    db = SessionLocal()
    processed: List[Dict[str, Any]] = []
    try:
        jobs = (
            db.query(Job)
            .filter(Job.status == JobStatus.QUEUED.value)
            .order_by(Job.created_at.asc())
            .limit(limit)
            .all()
        )
        for job in jobs:
            payload = job.payload_json or {}
            work_item_id = payload.get("work_item_id")
            item = None
            if work_item_id:
                item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
            if not item:
                job.status = JobStatus.FAILED.value
                processed.append({"job_id": job.id, "status": "failed", "reason": "work_item_missing"})
                continue

            result = _execute_action_plan(item, job)
            job.status = JobStatus.SUCCEEDED.value
            item.status = "completed"
            details = item.details or {}
            details["executed_at"] = result["executed_at"]
            details["job_status"] = job.status
            item.details = details
            processed.append({"job_id": job.id, "status": job.status, "work_item_id": item.id})

        db.commit()
    finally:
        db.close()
    return {"processed": processed, "count": len(processed)}
