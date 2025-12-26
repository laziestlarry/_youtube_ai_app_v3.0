"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Content Idea Schemas
class ContentIdeaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    priority: int = Field(default=5, ge=1, le=10)

class ContentIdeaResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: str
    priority: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Video Schemas
class VideoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: str = Field(..., min_length=1, max_length=50)
    script: Optional[str] = Field(None, max_length=10000)
    duration: int = Field(default=0, ge=0)

class VideoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: str
    duration: int
    views: int = 0
    likes: int = 0
    comments: int = 0
    revenue: float = 0.0
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_videos: int
    total_views: int
    total_revenue: float
    avg_engagement_rate: float
    top_performing_videos: List[Dict[str, Any]]
    revenue_by_category: Dict[str, float]

# Upload Schemas
class UploadResponse(BaseModel):
    upload_url: str
    file_name: str
    expires_at: datetime

# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Success Schemas
class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None