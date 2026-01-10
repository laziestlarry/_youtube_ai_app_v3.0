from typing import Any, Dict
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_db
from backend.services.outcome_service import OutcomeService
from backend.services.revenue_sync_service import RevenueSyncService


router = APIRouter()
service = OutcomeService()
sync_service = RevenueSyncService()
logger = logging.getLogger(__name__)


@router.get("/summary")
async def get_outcome_summary(
    session: AsyncSession = Depends(get_async_db),
) -> Dict[str, Any]:
    return await service.summary(session)


@router.post("/sync")
async def sync_outcomes(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_async_db),
) -> Dict[str, Any]:
    return await sync_service.sync(session, lookback_days=days)


@router.get("/health")
async def outcome_health(
    unknown_ratio_threshold: float = Query(0.5, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_async_db),
) -> Dict[str, Any]:
    summary = await service.summary(session)
    kpi_summary = summary.get("kpi", {}).get("summary", {})
    total = float(kpi_summary.get("total") or 0)
    unknown = float(kpi_summary.get("unknown") or 0)
    unknown_ratio = (unknown / total) if total else 1.0

    revenue = summary.get("revenue", {})
    last_24h = float(revenue.get("last_24h") or 0.0)
    last_7d = float(revenue.get("last_7d") or 0.0)
    last_30d = float(revenue.get("last_30d") or 0.0)

    issues = []
    status = "healthy"
    if unknown_ratio >= unknown_ratio_threshold:
        issues.append("KPI unknown ratio above threshold")
        status = "degraded"
    if last_7d <= 0 and last_30d <= 0:
        issues.append("Revenue inactive in the last 30 days")
        status = "degraded"
    if last_24h <= 0 and last_7d > 0:
        issues.append("No revenue in last 24h")

    if issues:
        logger.warning("Outcome health degraded: %s", "; ".join(issues))

    return {
        "status": status,
        "issues": issues,
        "unknown_ratio": unknown_ratio,
        "kpi_summary": kpi_summary,
        "revenue": {
            "last_24h": last_24h,
            "last_7d": last_7d,
            "last_30d": last_30d,
        },
        "updated_at": summary.get("updated_at"),
    }
