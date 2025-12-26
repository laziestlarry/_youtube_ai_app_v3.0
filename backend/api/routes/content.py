"""
Content Management API Routes
Core functionality for content creation and management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime

from backend.core.database import get_async_db as get_db
from backend.models.video import Video
from backend.models.content import ContentIdea
from backend.services.ai_service import AIService
from backend.core.schemas import VideoCreate, VideoResponse, ContentIdeaCreate, ContentIdeaResponse

router = APIRouter()

@router.post("/content-ideas", response_model=ContentIdeaResponse)
async def create_content_idea(
    idea: ContentIdeaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new content idea."""
    try:
        db_idea = ContentIdea(
            id=str(uuid.uuid4()),
            title=idea.title,
            description=idea.description,
            category=idea.category,
            priority=idea.priority,
            status="pending"
        )
        
        db.add(db_idea)
        await db.commit()
        await db.refresh(db_idea)
        
        return ContentIdeaResponse(
            id=db_idea.id,
            title=db_idea.title,
            description=db_idea.description,
            category=db_idea.category,
            priority=db_idea.priority,
            status=db_idea.status,
            created_at=db_idea.created_at
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create content idea: {str(e)}")

@router.get("/content-ideas", response_model=List[ContentIdeaResponse])
async def get_content_ideas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all content ideas."""
    try:
        result = await db.execute(
            select(ContentIdea)
            .offset(skip)
            .limit(limit)
            .order_by(ContentIdea.priority.desc(), ContentIdea.created_at.desc())
        )
        ideas = result.scalars().all()
        
        return [
            ContentIdeaResponse(
                id=idea.id,
                title=idea.title,
                description=idea.description,
                category=idea.category,
                priority=idea.priority,
                status=idea.status,
                created_at=idea.created_at
            )
            for idea in ideas
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content ideas: {str(e)}")

@router.post("/content-ideas/{idea_id}/generate")
async def generate_content_from_idea(
    idea_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate video content from a content idea."""
    try:
        # Get the content idea
        result = await db.execute(select(ContentIdea).where(ContentIdea.id == idea_id))
        idea = result.scalar_one_or_none()
        
        if not idea:
            raise HTTPException(status_code=404, detail="Content idea not found")
        
        # Generate content using AI
        ai_service = AIService()
        generated_content = await ai_service.generate_video_content(
            title=idea.title,
            description=idea.description,
            category=idea.category
        )
        
        # Update idea with generated content
        idea.generated_content = generated_content
        idea.status = "generated"
        idea.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "success",
            "message": "Content generated successfully",
            "data": generated_content
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}")

@router.post("/videos", response_model=VideoResponse)
async def create_video(
    video: VideoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new video."""
    try:
        db_video = Video(
            id=str(uuid.uuid4()),
            title=video.title,
            description=video.description,
            category=video.category,
            script=video.script,
            duration=video.duration,
            status="draft"
        )
        
        db.add(db_video)
        await db.commit()
        await db.refresh(db_video)
        
        return VideoResponse(
            id=db_video.id,
            title=db_video.title,
            description=db_video.description,
            category=db_video.category,
            duration=db_video.duration,
            status=db_video.status,
            created_at=db_video.created_at
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create video: {str(e)}")

@router.get("/videos", response_model=List[VideoResponse])
async def get_videos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all videos with optional status filter."""
    try:
        query = select(Video).offset(skip).limit(limit).order_by(Video.created_at.desc())
        
        if status:
            query = query.where(Video.status == status)
        
        result = await db.execute(query)
        videos = result.scalars().all()
        
        return [
            VideoResponse(
                id=video.id,
                title=video.title,
                description=video.description,
                category=video.category,
                duration=video.duration,
                views=video.views,
                likes=video.likes,
                comments=video.comments,
                revenue=video.revenue,
                status=video.status,
                created_at=video.created_at
            )
            for video in videos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")

@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific video by ID."""
    try:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse(
            id=video.id,
            title=video.title,
            description=video.description,
            category=video.category,
            duration=video.duration,
            views=video.views,
            likes=video.likes,
            comments=video.comments,
            revenue=video.revenue,
            status=video.status,
            created_at=video.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch video: {str(e)}")