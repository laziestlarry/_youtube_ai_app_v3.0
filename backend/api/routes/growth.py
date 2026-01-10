from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.core.database import get_db
from modules.growth_engine_v1.ingest import IngestionService
from modules.growth_engine_v1.catalog import CatalogService
from modules.growth_engine_v1.analytics import AnalyticsService
from modules.growth_engine_v1.automation import AnomalyService
# Import models to ensure they are registered
import modules.growth_engine_v1.models

router = APIRouter()

class IngestRequest(BaseModel):
    data: Dict[str, Any]
    provenance: Optional[Dict[str, Any]] = {
        "origin_name": "API", 
        "license": "open", 
        "quality_score": 1.0
    }

@router.post("/seed")
def seed_catalog(count: int = 60, db: Session = Depends(get_db)):
    """Generate Minimum Lovable SKUs (Growth Engine)."""
    service = CatalogService(db)
    return service.seed_initial_catalog(count)

@router.get("/catalog")
def list_catalog(db: Session = Depends(get_db)):
    """List all Growth SKUs."""
    service = CatalogService(db)
    return service.get_catalog()

@router.post("/ingest/{topic}", status_code=202)
def ingest_data(topic: str, payload: IngestRequest, db: Session = Depends(get_db)):
    """
    Ingest data into the Growth Engine.
    """
    service = IngestionService(db)
    try:
        result = service.ingest_generic(topic, payload.data, payload.provenance)
        return {"accepted": True, "result": result}
    except Exception as e:
        print(f"Ingest Error: {e}")
        return {"accepted": False, "error": str(e)}

@router.get("/dashboard/kpi")
def get_kpis(db: Session = Depends(get_db)):
    """Real-time KPI read for 'Daily Net Revenue'."""
    service = AnalyticsService(db)
    return service.get_kpi_summary()

@router.get("/dashboard/series")
def get_series(db: Session = Depends(get_db)):
    """Time-series data for analysis."""
    service = AnalyticsService(db)
    return service.get_chart_series()

@router.get("/dashboard/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """System Health & Anomalies."""
    service = AnomalyService(db)
    return {"alerts": service.check_anomalies()}
