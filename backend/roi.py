# backend/roi.py
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

class ROICalcRequest(BaseModel):
    views: int
    cpm: float  # USD per 1000 views

@router.post("/roi")
def calculate_roi(data: ROICalcRequest):
    earnings = (data.views / 1000) * data.cpm
    return {
        "estimated_earnings": round(earnings, 2),
        "input": {"views": data.views, "cpm": data.cpm}
    }
