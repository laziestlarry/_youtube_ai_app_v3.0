from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from backend.core.database import get_async_db
from backend.models.workflow import WorkflowColumn, WorkflowCard
from pydantic import BaseModel

router = APIRouter()

# Schemas
class CardCreate(BaseModel):
    title: str
    description: str = None
    column_id: int
    order: int = 0

class ColumnResponse(BaseModel):
    id: int
    name: str
    order: int
    class Config: from_attributes = True

class CardResponse(BaseModel):
    id: int
    title: str
    column_id: int
    order: int
    class Config: from_attributes = True

@router.get("/columns", response_model=List[ColumnResponse])
async def get_columns(db: AsyncSession = Depends(get_async_db)):
    """Get all workflow columns."""
    result = await db.execute(select(WorkflowColumn).order_by(WorkflowColumn.order))
    return result.scalars().all()

@router.post("/columns", response_model=ColumnResponse)
async def create_column(name: str, order: int = 0, db: AsyncSession = Depends(get_async_db)):
    """Create a new column."""
    col = WorkflowColumn(name=name, order=order)
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return col

@router.get("/cards", response_model=List[CardResponse])
async def get_cards(column_id: int = None, db: AsyncSession = Depends(get_async_db)):
    """Get all cards, optionally filtered by column."""
    query = select(WorkflowCard).order_by(WorkflowCard.order)
    if column_id:
        query = query.where(WorkflowCard.column_id == column_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/cards", response_model=CardResponse)
async def create_card(card: CardCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new card."""
    db_card = WorkflowCard(**card.dict())
    db.add(db_card)
    await db.commit()
    await db.refresh(db_card)
    return db_card

@router.patch("/cards/{card_id}/move")
async def move_card(card_id: int, column_id: int, order: int, db: AsyncSession = Depends(get_async_db)):
    """Move a card to a different column or change its order."""
    result = await db.execute(select(WorkflowCard).where(WorkflowCard.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card.column_id = column_id
    card.order = order
    await db.commit()
    return {"status": "success"}
