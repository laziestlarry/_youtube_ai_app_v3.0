from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_db
from backend.models.bizop import BizOpportunity
from backend.services.bizop_service import BizOpportunityService

router = APIRouter()


class BizOpportunityResponse(BaseModel):
    opportunityName: str
    description: Optional[str]
    potential: Optional[str]
    risk: Optional[str]
    quickReturn: Optional[str]
    priority: Optional[str]
    imageUrl: Optional[str]
    source: Optional[str]
    sourceId: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    rationale: Optional[str]


class BizOpportunityRefreshResponse(BaseModel):
    inserted: int
    updated: int
    total: int


@router.get("/opportunities", response_model=List[BizOpportunityResponse])
async def list_opportunities(
    source: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_async_db),
):
    service = BizOpportunityService()
    opportunities = await service.list_opportunities(session=session, source=source, limit=limit)
    return [
        BizOpportunityResponse(
            opportunityName=row.title,
            description=row.description,
            potential=row.potential,
            risk=row.risk,
            quickReturn=row.quick_return,
            priority=row.priority,
            imageUrl=row.image_url,
            source=row.source,
            sourceId=row.source_id,
            tags=row.tags,
            metadata=row.metadata_json,
            rationale=row.rationale,
        )
        for row in opportunities
    ]


@router.post("/refresh", response_model=BizOpportunityRefreshResponse)
async def refresh_opportunities(session: AsyncSession = Depends(get_async_db)):
    service = BizOpportunityService()
    try:
        result = await service.sync_from_sources(session=session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bizop refresh failed: {exc}") from exc
    return BizOpportunityRefreshResponse(**result)


@router.get("/sources", response_model=List[str])
async def list_sources(session: AsyncSession = Depends(get_async_db)):
    result = await session.execute(BizOpportunity.__table__.select().with_only_columns(BizOpportunity.source).distinct())
    return [row[0] for row in result.fetchall() if row[0]]
