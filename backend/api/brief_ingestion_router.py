from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from ..ai_modules.video_pipeline_enhanced import EnhancedVideoPipeline, PipelineResult
from backend.models import APIResponse
# from ..auth.dependencies import get_current_user # Assuming you have auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Video Brief Ingestion"])

class VideoBriefRequest(BaseModel):
    """
    Request model for initiating a video creation pipeline from a brief.

    Attributes:
        title: The title of the video.
        topic: Main topic or description for the video.
        category: Category of the video (e.g., "tech", "education").
        commercial_angle: Specific commercial focus (e.g., "affiliate marketing", "product review").
        source: Origin of the brief (e.g., "youtube-income-commander-mini", "manual_api").
        priority_score: Priority for processing this video (1-10, higher is more important).
        target_views: Estimated target views for the video.
        monetization_enabled: Whether monetization should be enabled for this video.
        quality_level: Desired output quality ("low", "medium", "high").
        custom_instructions: Dictionary for any additional specific instructions.
    """
    title: str = Field(..., description="The title of the video to be created.")
    topic: str = Field(..., description="The main topic or description for the video content.")
    category: Optional[str] = Field("general", description="Category of the video.")
    commercial_angle: Optional[str] = Field(None, description="Specific commercial angle or monetization focus.")
    source: Optional[str] = Field("api", description="Source of the video brief (e.g., 'youtube-income-commander-mini').")
    priority_score: Optional[int] = Field(5, ge=1, le=10, description="Priority score for the video creation (1-10).")
    target_views: Optional[int] = Field(10000, ge=100, description="Target views for the video.")
    monetization_enabled: Optional[bool] = Field(True, description="Whether monetization should be enabled.")
    quality_level: Optional[str] = Field("high", description="Desired quality level (e.g., 'low', 'medium', 'high').")
    custom_instructions: Optional[Dict[str, Any]] = Field(None, description="Any custom instructions for the pipeline.")

async def run_pipeline_background(pipeline: EnhancedVideoPipeline):
    """
    Asynchronously runs the video generation pipeline in the background.

    This function is intended to be called by `BackgroundTasks` to avoid
    blocking the API response.

    Args:
        pipeline (EnhancedVideoPipeline): The pipeline instance to execute.
    """
    try:
        await pipeline.execute_full_pipeline()
        logger.info(f"Background pipeline {pipeline.pipeline_id} execution finished.")
    except Exception as e:
        logger.error(f"Error in background pipeline {pipeline.pipeline_id}: {e}")
        # Optionally, update pipeline status in DB to 'error' here

@router.post("/api/v1/initiate-video-from-brief", response_model=APIResponse)
async def initiate_video_from_brief(
    brief: VideoBriefRequest,
    background_tasks: BackgroundTasks,
    # current_user: Any = Depends(get_current_user) # Uncomment if auth is needed
):
    """
    Accepts a video brief and initiates the video creation pipeline as a background task.

    This endpoint allows external systems (like `youtube-income-commander-mini`) or
    manual API calls to trigger the automated video generation process.

    Args:
        brief (VideoBriefRequest): The video brief containing details for content creation.
        background_tasks (BackgroundTasks): FastAPI's background task manager.
        current_user (Any, optional): Authenticated user object (if authentication is enabled).

    Returns:
        APIResponse: A response indicating the pipeline has been initiated,
                     including the `pipeline_id` for status tracking.

    Raises:
        HTTPException: If there's an error during pipeline initiation.
    """
    try:
        logger.info(f"Received video brief: {brief.title}")

        pipeline = EnhancedVideoPipeline(
            topic=brief.topic,
            title=brief.title,
            target_views=brief.target_views,
            monetization_enabled=brief.monetization_enabled,
            quality_level=brief.quality_level
        )

        # Enhance pipeline metadata with more brief details
        pipeline.metadata.update({
            "brief_category": brief.category,
            "brief_commercial_angle": brief.commercial_angle,
            "brief_source": brief.source,
            "brief_priority_score": brief.priority_score,
            "brief_custom_instructions": brief.custom_instructions
        })

        background_tasks.add_task(run_pipeline_background, pipeline)

        return APIResponse(
            status="success",
            data={"pipeline_id": pipeline.pipeline_id, "message": "Video creation pipeline initiated."},
            message="Video creation process started in the background."
        )
    except Exception as e:
        logger.error(f"Failed to initiate video pipeline from brief: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")