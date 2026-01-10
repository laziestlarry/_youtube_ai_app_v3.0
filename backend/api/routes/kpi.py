from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.kpi_service import KPIService
from backend.core.database import get_async_db

router = APIRouter()
service = KPIService()


class KPIUpdateItem(BaseModel):
    id: str
    actual: float
    note: Optional[str] = None


class KPIUpdateRequest(BaseModel):
    updates: List[KPIUpdateItem]


@router.get("/targets")
async def get_kpi_targets(session: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    return await service.list_kpis_async(session)


@router.get("/summary")
async def get_kpi_summary(session: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    payload = await service.list_kpis_async(session)
    return {"updated_at": payload.get("updated_at"), "summary": payload.get("summary", {})}


@router.post("/targets")
async def update_kpi_targets(
    payload: KPIUpdateRequest,
    session: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    updated = service.update_actuals([item.model_dump() for item in payload.updates])
    summary = (await service.list_kpis_async(session)).get("summary", {})
    return {"updated": updated, "summary": summary}
