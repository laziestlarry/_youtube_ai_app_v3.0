import os
from fastapi import APIRouter, Depends, Header, HTTPException

from autonomax.app.main import (
    SessionLocal,
    mission_summary,
    mission_focus,
    run_missions,
    complete_job,
    import_blueprints,
    import_affiliates,
    register_influencer,
    bind_protocol,
)
from autonomax.workflows.executor import run_job_queue

router = APIRouter()


def _guard(token: str | None) -> None:
    expected = os.getenv("MISSION_SCHEDULE_TOKEN")
    if not expected:
        return
    if not token or token != expected:
        raise HTTPException(status_code=403, detail="Invalid mission token")


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def get_summary(db=Depends(_get_db)):
    return mission_summary(db=db)


@router.get("/focus")
def get_focus(db=Depends(_get_db)):
    return mission_focus(db=db)


@router.post("/run")
def run_schedule(
    limit: int = 5,
    dry_run: bool = False,
    x_autonomax_token: str | None = Header(default=None),
    db=Depends(_get_db),
):
    _guard(x_autonomax_token)
    return run_missions(limit=limit, dry_run=dry_run, db=db)


@router.post("/execute")
def execute_jobs(
    limit: int = 5,
    x_autonomax_token: str | None = Header(default=None),
):
    _guard(x_autonomax_token)
    return run_job_queue(limit=limit)


@router.post("/dispatch")
def dispatch_missions(
    limit: int = 5,
    x_autonomax_token: str | None = Header(default=None),
    db=Depends(_get_db),
):
    _guard(x_autonomax_token)
    scheduled = run_missions(limit=limit, dry_run=False, db=db)
    executed = run_job_queue(limit=limit)
    return {"scheduled": scheduled, "executed": executed}


@router.post("/seed")
def seed_missions(
    x_autonomax_token: str | None = Header(default=None),
    db=Depends(_get_db),
):
    _guard(x_autonomax_token)
    uploads_root = os.getenv("MISSION_UPLOADS_PATH", "/app/uploads")
    blueprint_path = os.path.join(
        uploads_root,
        "AI Automation System Blueprint & Setup - AI Automation System Blueprint & Setup.csv",
    )
    affiliate_path = os.path.join(
        uploads_root,
        "Affiliate Products - RMS - Sheet1.csv",
    )
    results = {
        "blueprints": import_blueprints(path=blueprint_path, db=db),
        "affiliates": import_affiliates(path=affiliate_path, db=db),
    }
    influencer_name = os.getenv("MISSION_INFLUENCER_NAME")
    influencer_channel = os.getenv("MISSION_INFLUENCER_CHANNEL")
    influencer_email = os.getenv("MISSION_INFLUENCER_EMAIL")
    if influencer_name and influencer_channel:
        results["influencer"] = register_influencer(
            {
                "name": influencer_name,
                "channel_url": influencer_channel,
                "contact_email": influencer_email,
                "notes": "Seeded from environment.",
            },
            db=db,
        )
    protocol_path = os.getenv("MISSION_PROTOCOL_PATH")
    if protocol_path and os.path.isdir(protocol_path):
        results["protocol_binding"] = bind_protocol(
            {"target_path": protocol_path, "protocol_name": "united"},
            db=db,
        )
    return results


@router.post("/jobs/complete")
def finish_job(
    job_id: int,
    status: str = "succeeded",
    x_autonomax_token: str | None = Header(default=None),
    db=Depends(_get_db),
):
    _guard(x_autonomax_token)
    return complete_job(job_id=job_id, status=status, db=db)
