from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.api.deps import get_current_user
from backend.core.database import get_async_db
from backend.services.youtube_service import YouTubeService
from backend.models.user import User

router = APIRouter()
youtube_service = YouTubeService()

@router.get("/auth-url")
async def get_auth_url(current_user: User = Depends(get_current_user)):
    """Generate YouTube OAuth login URL."""
    try:
        url = youtube_service.get_login_url()
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def youtube_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """Handle YouTube OAuth callback."""
    try:
        # Exchange code for token
        result = await youtube_service.exchange_code_for_token(code, current_user.id, db)
        
        # Trigger background data sync
        # Note: credentials are now in the DB or we can pass some info
        # For simplicity, we can let the service fetch them or just trigger a sync
        # Since exchange_code_for_token already called it once, this is for future periodic syncs
        # or we just rely on that first call.
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels")
async def get_channels(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get connected channels for current user."""
    # This will be implemented to fetch from DB
    return {"channels": []}
