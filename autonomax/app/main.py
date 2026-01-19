from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import (
    Base,
    Job,
    JobStatus,
    Product,
    AutomationBlueprint,
    AffiliateProgram,
    InfluencerSource,
    WorkflowExtraction,
    ProtocolBinding,
    WorkItem,
)
from datetime import datetime, timedelta
import csv
import os
import re
from typing import Dict, Any, List

# Database Setup (SQLite for local speed, overridable for schedules)
SQLALCHEMY_DATABASE_URL = os.getenv("AUTONOMAX_DB_URL", "sqlite:///./autonomax.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonoma-X Commander")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/jobs/enqueue")
def enqueue_job(job_type: str, payload: dict, db: Session = Depends(get_db)):
    job = Job(type=job_type, payload_json=payload)
    db.add(job)
    db.commit()
    return {"job_id": job.id, "status": "queued"}

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    product_count = db.query(Product).count()
    job_queue = db.query(Job).filter(Job.status == "queued").count()
    work_items = db.query(WorkItem).count()
    focus_items = db.query(WorkItem).filter(WorkItem.focus == 1, WorkItem.status == "scheduled").count()
    return {
        "products_live": product_count,
        "jobs_pending": job_queue,
        "work_items": work_items,
        "focus_items": focus_items,
    }

def _parse_volume(value: str) -> int:
    if not value:
        return 0
    text = value.lower().replace(",", "").strip()
    multiplier = 1
    if "m" in text:
        multiplier = 1_000_000
    elif "k" in text:
        multiplier = 1_000
    match = re.search(r"(\d+(\.\d+)?)", text)
    if not match:
        return 0
    return int(float(match.group(1)) * multiplier)

def _parse_price(value: str) -> float:
    if not value:
        return 0.0
    text = value.replace("$", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0

def _parse_percent(value: str) -> float:
    if not value:
        return 0.0
    text = value.strip().replace("%", "")
    try:
        return float(text) / 100.0
    except ValueError:
        return 0.0

def _priority_score(volume: int, price: float, recurring_bonus: float = 0.0) -> float:
    base = float(volume) * float(price)
    score = base / 1000.0
    if recurring_bonus:
        score *= 1.0 + recurring_bonus
    return round(min(score, 100.0), 2)

def _ensure_work_item(
    db: Session,
    title: str,
    category: str,
    source_type: str,
    source_ref: str,
    priority_score: float,
    due_at: datetime,
    focus: int,
    details: Dict[str, Any],
) -> WorkItem:
    existing = db.query(WorkItem).filter_by(
        source_type=source_type,
        source_ref=source_ref,
        category=category,
    ).first()
    if existing:
        existing.priority_score = priority_score
        existing.due_at = due_at
        existing.focus = focus
        existing.details = details
        return existing
    item = WorkItem(
        title=title,
        category=category,
        status="scheduled",
        priority_score=priority_score,
        focus=focus,
        due_at=due_at,
        source_type=source_type,
        source_ref=source_ref,
        details=details,
    )
    db.add(item)
    return item

def _build_action_plan(item: WorkItem) -> Dict[str, Any]:
    details = item.details or {}
    if item.category == "completion":
        steps = [
            "Finalize asset pack and verify delivery link.",
            "Publish listing and validate pricing.",
            "Trigger first promotion burst.",
        ]
        success = "Listing live with verified delivery and first click-through."
    elif item.category == "upgrade":
        steps = [
            "Improve listing copy and creatives.",
            "Run price/offer split test.",
            "Update FAQ and support snippet.",
        ]
        success = "Conversion rate improves by 10% over baseline."
    elif item.category == "modernization":
        steps = [
            "Automate intake or fulfillment step.",
            "Instrument tracking and alerts.",
            "Backfill KPIs into dashboard.",
        ]
        success = "Task runs without manual intervention for 7 days."
    elif item.category == "workflow_extraction":
        steps = [
            "Summarize influencer workflow in 5-7 steps.",
            "Map steps to internal automation triggers.",
            "Create repeatable checklist for launch.",
        ]
        success = "Workflow checklist created and mapped to tasks."
    else:
        steps = ["Review task details and define next action."]
        success = "Next action defined."
    return {
        "steps": steps,
        "success_signal": success,
        "details": details,
    }

def _enqueue_job_for_item(db: Session, item: WorkItem, action_plan: Dict[str, Any]) -> Job:
    job = Job(
        type=f"mission_{item.category}",
        payload_json={
            "work_item_id": item.id,
            "title": item.title,
            "category": item.category,
            "source_type": item.source_type,
            "source_ref": item.source_ref,
            "action_plan": action_plan,
        },
    )
    db.add(job)
    db.flush()
    return job

@app.post("/imports/blueprints")
def import_blueprints(path: str = None, db: Session = Depends(get_db)):
    csv_path = path or os.getenv(
        "BLUEPRINT_CSV_PATH",
        "uploads/AI Automation System Blueprint & Setup - AI Automation System Blueprint & Setup.csv",
    )
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail=f"Blueprint CSV not found: {csv_path}")

    rows: List[AutomationBlueprint] = []
    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            keyword = (row.get("Keyword / Niche") or "").strip().strip("\"")
            if not keyword:
                continue
            est_volume_raw = (row.get("Est. Vol") or "").strip()
            avg_price_raw = (row.get("Avg Price") or "").strip()
            competitors = (row.get("Competitors") or "").strip()
            winning_hook = (row.get("Winning Hook (Title)") or "").strip()

            est_volume = _parse_volume(est_volume_raw)
            avg_price = _parse_price(avg_price_raw)
            priority = _priority_score(est_volume, avg_price)
            revenue_potential = float(est_volume) * float(avg_price)

            blueprint = db.query(AutomationBlueprint).filter_by(keyword_niche=keyword).first()
            if not blueprint:
                blueprint = AutomationBlueprint(keyword_niche=keyword)
                db.add(blueprint)
            blueprint.est_volume_raw = est_volume_raw
            blueprint.avg_price_raw = avg_price_raw
            blueprint.competitors = competitors
            blueprint.winning_hook = winning_hook
            blueprint.est_volume = est_volume
            blueprint.avg_price_usd = avg_price
            blueprint.revenue_potential = revenue_potential
            blueprint.priority_score = priority
            rows.append(blueprint)

    db.commit()

    rows_sorted = sorted(rows, key=lambda item: item.priority_score, reverse=True)
    focus_keys = {item.keyword_niche for item in rows_sorted[:3]}
    now = datetime.utcnow()
    for blueprint in rows_sorted:
        focus = 1 if blueprint.keyword_niche in focus_keys else 0
        details = {
            "volume": blueprint.est_volume,
            "avg_price": blueprint.avg_price_usd,
            "competitors": blueprint.competitors,
            "winning_hook": blueprint.winning_hook,
        }
        _ensure_work_item(
            db,
            title=f"Completion: Launch {blueprint.keyword_niche} asset set",
            category="completion",
            source_type="blueprint",
            source_ref=blueprint.keyword_niche,
            priority_score=blueprint.priority_score,
            due_at=now + timedelta(days=3),
            focus=focus,
            details=details,
        )
        _ensure_work_item(
            db,
            title=f"Upgrade: Optimize listings for {blueprint.keyword_niche}",
            category="upgrade",
            source_type="blueprint",
            source_ref=blueprint.keyword_niche,
            priority_score=max(blueprint.priority_score - 10, 0),
            due_at=now + timedelta(days=7),
            focus=0,
            details=details,
        )
        _ensure_work_item(
            db,
            title=f"Modernize: Automate content pipeline for {blueprint.keyword_niche}",
            category="modernization",
            source_type="blueprint",
            source_ref=blueprint.keyword_niche,
            priority_score=max(blueprint.priority_score - 20, 0),
            due_at=now + timedelta(days=14),
            focus=0,
            details=details,
        )
    db.commit()

    return {"imported": len(rows_sorted), "focus": len(focus_keys), "csv_path": csv_path}

@app.post("/imports/affiliates")
def import_affiliates(path: str = None, db: Session = Depends(get_db)):
    csv_path = path or os.getenv(
        "AFFILIATE_CSV_PATH",
        "uploads/Affiliate Products - RMS - Sheet1.csv",
    )
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail=f"Affiliate CSV not found: {csv_path}")

    programs: List[AffiliateProgram] = []
    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = (row.get("Affiliate Program") or "").strip()
            if not name:
                continue
            signup_url = (row.get("Sign Up Link") or "").strip()
            category = (row.get("Category") or "").strip()
            commission_raw = (row.get("Comission") or "").strip()
            recurring = (row.get("Recurring") or "No").strip()
            commission_rate = _parse_percent(commission_raw)
            recurring_bonus = 0.25 if recurring.lower() == "yes" else 0.0
            priority = _priority_score(10_000, commission_rate * 100.0, recurring_bonus=recurring_bonus)

            program = db.query(AffiliateProgram).filter_by(name=name).first()
            if not program:
                program = AffiliateProgram(name=name)
                db.add(program)
            program.signup_url = signup_url
            program.category = category
            program.commission_raw = commission_raw
            program.commission_rate = commission_rate
            program.recurring = recurring
            programs.append(program)

    db.commit()

    programs_sorted = sorted(programs, key=lambda item: item.commission_rate or 0.0, reverse=True)
    focus_names = {item.name for item in programs_sorted[:3]}
    now = datetime.utcnow()
    for program in programs_sorted:
        focus = 1 if program.name in focus_names else 0
        details = {
            "signup_url": program.signup_url,
            "category": program.category,
            "commission": program.commission_raw,
            "recurring": program.recurring,
        }
        priority = _priority_score(10_000, (program.commission_rate or 0.0) * 100.0, recurring_bonus=0.25)
        _ensure_work_item(
            db,
            title=f"Completion: Activate affiliate program {program.name}",
            category="completion",
            source_type="affiliate",
            source_ref=program.name,
            priority_score=priority,
            due_at=now + timedelta(days=2),
            focus=focus,
            details=details,
        )
        _ensure_work_item(
            db,
            title=f"Upgrade: Build content funnel for {program.name}",
            category="upgrade",
            source_type="affiliate",
            source_ref=program.name,
            priority_score=max(priority - 10, 0),
            due_at=now + timedelta(days=5),
            focus=0,
            details=details,
        )
        _ensure_work_item(
            db,
            title=f"Modernize: Automate tracking + reporting for {program.name}",
            category="modernization",
            source_type="affiliate",
            source_ref=program.name,
            priority_score=max(priority - 20, 0),
            due_at=now + timedelta(days=10),
            focus=0,
            details=details,
        )
    db.commit()

    return {"imported": len(programs_sorted), "focus": len(focus_names), "csv_path": csv_path}

@app.post("/workflows/influencer")
def register_influencer(payload: Dict[str, Any], db: Session = Depends(get_db)):
    name = (payload.get("name") or "").strip()
    channel_url = (payload.get("channel_url") or "").strip()
    if not name or not channel_url:
        raise HTTPException(status_code=400, detail="name and channel_url are required")
    contact_email = (payload.get("contact_email") or "").strip()
    notes = (payload.get("notes") or "").strip()
    guidelines = payload.get("guidelines")

    source = InfluencerSource(
        name=name,
        channel_url=channel_url,
        contact_email=contact_email,
        notes=notes,
        status="queued" if not guidelines else "reviewed",
    )
    db.add(source)
    db.commit()

    extraction = WorkflowExtraction(
        source_type="influencer",
        source_ref=name,
        steps_json=guidelines or {"status": "pending_extraction"},
        status="queued" if not guidelines else "completed",
    )
    db.add(extraction)

    now = datetime.utcnow()
    _ensure_work_item(
        db,
        title=f"Workflow extraction: {name} YouTube playbook",
        category="workflow_extraction",
        source_type="influencer",
        source_ref=name,
        priority_score=80.0,
        due_at=now + timedelta(days=4),
        focus=1,
        details={"channel_url": channel_url, "contact_email": contact_email},
    )
    db.commit()
    return {"influencer_id": source.id, "workflow_id": extraction.id}

def _scan_protocol_files(target_path: str) -> Dict[str, Any]:
    files = []
    summary_lines = []
    for entry in os.listdir(target_path):
        full_path = os.path.join(target_path, entry)
        if not os.path.isfile(full_path):
            continue
        _, ext = os.path.splitext(entry.lower())
        if ext not in (".txt", ".md", ".csv", ".json"):
            continue
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as handle:
                lines = [line.strip() for line in handle.readlines() if line.strip()]
        except OSError:
            lines = []
        files.append({"path": full_path, "lines": len(lines)})
        if lines:
            summary_lines.append(f"{entry}: {lines[0]}")
    summary = " | ".join(summary_lines[:5]) if summary_lines else "No protocol files detected."
    return {"files": files, "summary": summary}

@app.post("/protocols/bind")
def bind_protocol(payload: Dict[str, Any], db: Session = Depends(get_db)):
    target_path = (payload.get("target_path") or "").strip()
    protocol_name = (payload.get("protocol_name") or "united").strip()
    if not target_path or not os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="target_path must be a valid directory")

    scan = _scan_protocol_files(target_path)
    binding = ProtocolBinding(
        target_path=target_path,
        protocol_name=protocol_name,
        files_json=scan["files"],
        summary=scan["summary"],
    )
    db.add(binding)

    now = datetime.utcnow()
    _ensure_work_item(
        db,
        title=f"Binding extension: Apply {protocol_name} protocols to {os.path.basename(target_path)}",
        category="modernization",
        source_type="protocol",
        source_ref=protocol_name,
        priority_score=75.0,
        due_at=now + timedelta(days=6),
        focus=1,
        details={"target_path": target_path, "summary": scan["summary"]},
    )
    db.commit()
    return {"binding_id": binding.id, "files": len(scan["files"])}

@app.get("/missions/focus")
def mission_focus(db: Session = Depends(get_db)):
    items = db.query(WorkItem).filter(WorkItem.focus == 1).order_by(WorkItem.priority_score.desc()).all()
    return {
        "focus_items": [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "priority_score": item.priority_score,
                "due_at": item.due_at.isoformat() if item.due_at else None,
                "source_type": item.source_type,
                "source_ref": item.source_ref,
            }
            for item in items
        ]
    }

@app.get("/missions/summary")
def mission_summary(db: Session = Depends(get_db)):
    total = db.query(WorkItem).count()
    scheduled = db.query(WorkItem).filter(WorkItem.status == "scheduled").count()
    focus = db.query(WorkItem).filter(WorkItem.focus == 1).count()
    return {
        "total_items": total,
        "scheduled": scheduled,
        "focus_items": focus,
        "blueprints": db.query(AutomationBlueprint).count(),
        "affiliate_programs": db.query(AffiliateProgram).count(),
        "influencers": db.query(InfluencerSource).count(),
        "protocol_bindings": db.query(ProtocolBinding).count(),
    }

@app.post("/missions/run")
def run_missions(limit: int = 5, dry_run: bool = False, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    items = (
        db.query(WorkItem)
        .filter(WorkItem.status == "scheduled", WorkItem.due_at <= now)
        .order_by(WorkItem.focus.desc(), WorkItem.priority_score.desc(), WorkItem.due_at.asc())
        .limit(limit)
        .all()
    )
    if dry_run:
        return {
            "dry_run": True,
            "candidates": [
                {
                    "id": item.id,
                    "title": item.title,
                    "category": item.category,
                    "priority_score": item.priority_score,
                    "due_at": item.due_at.isoformat() if item.due_at else None,
                }
                for item in items
            ],
        }

    enqueued = []
    for item in items:
        action_plan = _build_action_plan(item)
        job = _enqueue_job_for_item(db, item, action_plan)
        details = item.details or {}
        details.update(
            {
                "job_id": job.id,
                "queued_at": now.isoformat(),
                "action_plan": action_plan,
            }
        )
        item.details = details
        item.status = "queued"
        enqueued.append(
            {
                "work_item_id": item.id,
                "job_id": job.id,
                "title": item.title,
            }
        )

    db.commit()
    return {"queued": enqueued, "count": len(enqueued)}

@app.post("/jobs/complete")
def complete_job(job_id: int, status: str = "succeeded", db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = status
    payload = job.payload_json or {}
    work_item_id = payload.get("work_item_id")
    if work_item_id:
        item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if item:
            item.status = "completed" if status == JobStatus.SUCCEEDED.value else "blocked"
            details = item.details or {}
            details["completed_at"] = datetime.utcnow().isoformat()
            item.details = details
    db.commit()
    return {"job_id": job.id, "status": job.status}
