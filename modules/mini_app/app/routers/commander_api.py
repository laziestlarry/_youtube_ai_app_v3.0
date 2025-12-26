from fastapi import APIRouter, HTTPException, Body
from typing import List

from ..models import (
    CommercialIdeaRequest, CommercialIdea,
    RevenueProjectionRequest, RevenueProjection,
    PipelineInitiationRequest
)
from ..services.idea_generator import CommercialIdeaGenerator
from ..services.revenue_projector import SimpleRevenueProjector
from ..services.pipeline_initiator import MainPipelineInitiator

router = APIRouter()
idea_gen_service = CommercialIdeaGenerator()
revenue_proj_service = SimpleRevenueProjector()
pipeline_init_service = MainPipelineInitiator()

@router.post("/generate-commercial-ideas", response_model=List[CommercialIdea])
async def generate_commercial_ideas_endpoint(request: CommercialIdeaRequest):
    try:
        ideas = await idea_gen_service.generate_ideas(request.niche, request.focus, request.count)
        return ideas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project-revenue", response_model=RevenueProjection)
async def project_revenue_endpoint(request: RevenueProjectionRequest):
    try:
        projection = await revenue_proj_service.project(
            request.title, request.niche, request.estimated_views, request.estimated_cpm
        )
        return projection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initiate-main-pipeline", response_model=dict)
async def initiate_main_pipeline_endpoint(request: PipelineInitiationRequest):
    try:
        result = await pipeline_init_service.initiate(request.idea, request.target_platform_url)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "app": "YouTube Income Commander Mini"}