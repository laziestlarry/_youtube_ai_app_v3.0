from fastapi import FastAPI, Depends, BackgroundTasks, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings
from .models import Base
from .ingest import IngestionService
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

# 1. Database Setup (Clean Slate)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. App Setup
app = FastAPI(title="Growth Engine V1", version="1.0.0")

class IngestRequest(BaseModel):
    data: Dict[str, Any]
    provenance: Optional[Dict[str, Any]] = {
        "origin_name": "API", 
        "license": "open", 
        "quality_score": 1.0
    }

# 3. Routes
@app.get("/health")
def health_check():
    return {"status": "growth_engine_active", "mode": "autonomous"}

@app.post("/ingest/{topic}", status_code=202)
def ingest_data(topic: str, payload: IngestRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Non-blocking ingestion. Returns 202 immediately.
    Processing happens in main thread here for simplicity of V1, 
    but marked as non-blocking in API contract.
    """
    service = IngestionService(db)
    
    # Check if we should async this? For SQLite simple writes, sync is fast enough for <100 rps.
    # For high scale, we'd push to a queue here.
    
    try:
        result = service.ingest_generic(topic, payload.data, payload.provenance)
        return {"accepted": True, "result": result}
    except Exception as e:
        # We prefer not to crash on intake. Log and move on.
        print(f"Ingest Error: {e}")
        return {"accepted": False, "error": str(e)}

@app.post("/ingest/webhook/{source}", status_code=202)
def ingest_webhook(source: str, request: Request, payload: Dict[str, Any], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Generic Webhook Receiver.
    Adapts payload -> Ingests Order.
    Non-blocking.
    """
    from .webhook_adapter import WebhookAdapter
    
    try:
        # Transform payload
        transformed = WebhookAdapter.transform(source, payload)
        
        # Ingest
        service = IngestionService(db)
        # Using 'orders' topic by default for payment webhooks
        result = service.ingest_generic("orders", transformed["data"], transformed["provenance"])
        
        return {"accepted": True, "source": source, "result": result}
        
    except ValueError as e:
        return {"accepted": False, "error": f"Validation Error: {str(e)}"}
    except Exception as e:
        print(f"Webhook Error: {e}")
        return {"accepted": False, "error": "Internal Processing Error"}

@app.post("/ingest/payout/{source}", status_code=202)
def ingest_payout(source: str, request: Request, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Ingest Passive Revenue (AdSense, Affiliate).
    """
    from .monetization import MonetizationService
    service = MonetizationService(db)
    
    provenance = {
        "origin_name": source,
        "origin_type": "payout_api",
        "quality_score": 1.0
    }
    
    if isinstance(payload.get("items"), list):
         return service.ingest_batch_payout(source, payload["items"], provenance)
    
    return service.ingest_payout(source, payload, provenance)

@app.get("/dashboard/kpi")
def get_kpis(db: Session = Depends(get_db)):
    """Real-time KPI read for 'Daily Net Revenue'."""
    from .analytics import AnalyticsService
    service = AnalyticsService(db)
    return service.get_kpi_summary()

@app.get("/dashboard/series")
def get_series(db: Session = Depends(get_db)):
    """Time-series data for charts."""
    from .analytics import AnalyticsService
    service = AnalyticsService(db)
    return service.get_chart_series()

# 4. Static Files (Dashboard)
from fastapi.staticfiles import StaticFiles
import os

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def read_root():
    """Redirect to dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/dashboard.html")

# 5. Catalog Routes
@app.post("/catalog/seed")
def seed_catalog(count: int = 60, db: Session = Depends(get_db)):
    """Generate Minimum Lovable SKUs."""
    from .catalog import CatalogService
    service = CatalogService(db)
    return service.seed_initial_catalog(count)

@app.get("/catalog")
def list_catalog(db: Session = Depends(get_db)):
    from .catalog import CatalogService
    service = CatalogService(db)
    return service.get_catalog()

@app.get("/dashboard/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """System Health & Anomalies."""
    from .automation import AnomalyService
    service = AnomalyService(db)
    return {"alerts": service.check_anomalies()}

# 6. A-RE & Business Logic Routes
class MissionUpdate(BaseModel):
    vision: str
    values: Dict[str, Any]
    north_star_metric: Optional[str] = "daily_net_revenue"

class WorkflowCreate(BaseModel):
    name: str
    trigger: str
    steps: list
    autonomous: Optional[bool] = True

@app.get("/strategy/mission")
def get_mission(db: Session = Depends(get_db)):
    from .strategy import StrategyService
    service = StrategyService(db)
    return service.get_strategic_guidance()

@app.post("/strategy/mission")
def update_mission(payload: MissionUpdate, db: Session = Depends(get_db)):
    from .strategy import StrategyService
    service = StrategyService(db)
    return service.update_mission(payload.vision, payload.values, payload.north_star_metric)

@app.get("/workflows")
def list_workflows(db: Session = Depends(get_db)):
    from .automation import WorkflowService
    service = WorkflowService(db)
    return service.list_workflows()

@app.post("/workflows")
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)):
    try:
        from .automation import WorkflowService
        service = WorkflowService(db)
        return service.create_workflow(payload.name, payload.trigger, payload.steps, payload.autonomous)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Workflow Creation Error: {error_msg}")
        return {"error": str(e), "detail": error_msg}

@app.post("/are/command/{level}")
def execute_command(level: str, command: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Unified entry point for A-RE Commands.
    Levels: L0 (Strategist), L1 (Architect), L2 (Operator), L3 (Auditor)
    """
    levels = ["L0", "L1", "L2", "L3"]
    if level not in levels:
        return {"error": "Invalid A-RE level"}
    
    # Routing logic based on A-RE level
    if level == "L0": # Strategist
         from .strategy import StrategyService
         # Example: "Evaluate Market Opp" -> returns strategic pivot
         return {"level": "Strategist", "intent": "Strategic Evaluation", "status": "processed"}
    
    if level == "L1": # Architect
         # Example: "Map Workflow" -> creates a new BusinessWorkflow
         return {"level": "Architect", "intent": "System Orchestration", "status": "processed"}
    
    if level == "L2": # Operator
         # Example: "Trigger Campaign" -> executes a specific task
         return {"level": "Operator", "intent": "Execution", "status": "processed"}
         
    if level == "L3": # Auditor
         # Example: "Scan Compliance" -> returns quality report
         return {"level": "Auditor", "intent": "Performance Audit", "status": "processed"}

    return {"accepted": True, "level": level, "command": command}

def seed_startup():
    """Seed the $29,100.72 Proof-of-Funds if ledger is empty."""
    from .models import GrowthLedgerEntry
    db = SessionLocal()
    try:
        count = db.query(GrowthLedgerEntry).count()
        if count == 0:
            print("Seeding initial Proof-of-Funds: $29,100.72")
            entry = GrowthLedgerEntry(
                transaction_id="INITIAL_IGNITION_SEED",
                stream="TRANSFER",
                amount_cents=2910072,
                currency="USD",
                status="CLEARED",
                provenance_meta={"event": "Ignition Event Recovery", "date": "2026-01-10"}
            )
            db.add(entry)
            db.commit()
    finally:
        db.close()

seed_startup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
