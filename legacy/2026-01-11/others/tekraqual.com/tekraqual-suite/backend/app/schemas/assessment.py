from typing import List, Optional
from pydantic import BaseModel


class AnswerCreate(BaseModel):
    question_id: int
    numeric_value: float
    raw_value: Optional[str] = None


class AssessmentCreate(BaseModel):
    organization_name: str


class DimensionScoreOut(BaseModel):
    dimension_id: int
    dimension_code: str
    dimension_name: str
    score: float
    level: Optional[str] = None

    class Config:
        orm_mode = True


class AssessmentOut(BaseModel):
    id: int
    organization_name: str
    status: str
    overall_score: Optional[float] = None
    readiness_level: Optional[str] = None
    dimension_scores: List[DimensionScoreOut] = []

    class Config:
        orm_mode = True

class GuidanceBlock(BaseModel):
  title: str
  body: str
  dimension_code: Optional[str] = None
  score: Optional[float] = None
  band: Optional[str] = None


class AssessmentReportOut(BaseModel):
  assessment: AssessmentOut
  summary: str
  strengths: List[GuidanceBlock]
  focus_areas: List[GuidanceBlock]
  next_90_days: List[GuidanceBlock]
  recommended_offers: List[GuidanceBlock]
