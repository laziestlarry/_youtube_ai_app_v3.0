from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CommercialIdeaRequest(BaseModel):
    niche: str = Field(..., description="Niche to generate ideas for")
    focus: str = Field("high_cpm", description="Focus for idea generation (e.g., high_cpm, affiliate_friendly)")
    count: int = Field(3, ge=1, le=10, description="Number of ideas to generate")

class CommercialIdea(BaseModel):
    title: str
    description: str
    commercial_angle: str
    estimated_cpm_range: Optional[str] = None # e.g., "$5-$15"
    keywords: List[str] = []

class RevenueProjectionRequest(BaseModel):
    title: str
    niche: str
    estimated_views: int = Field(10000, ge=1000)
    estimated_cpm: float = Field(5.0, ge=0.1) # Average CPM for the niche

class RevenueProjection(BaseModel):
    title: str
    projected_ad_revenue: float
    notes: str

class PipelineInitiationRequest(BaseModel):
    idea: CommercialIdea
    target_platform_url: Optional[str] = None # To override default if needed