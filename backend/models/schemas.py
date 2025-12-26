# schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class VideoIdea(BaseModel):
    title: str
    category: str
    expected_views: int

class VideoIdeaDB(BaseModel):
    id: int
    title: str
    category: str
    expected_views: int
    created_at: datetime
    status: str = "Draft"

    model_config = {
        "from_attributes": True
    }

class ROIRequest(BaseModel):
    views: int
    cpm: float = 5.0

class ROIResponse(BaseModel):
    estimated_views: int
    cpm: float
    estimated_revenue: float

class APIResponse(BaseModel):
    status: str = Field(..., description="Status of the API response")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")

class VideoIdeaCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    category: str = Field(..., min_length=2, max_length=50)
    expected_views: int = Field(..., ge=0)

class VideoIdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    expected_views: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, min_length=2, max_length=20)

class ScriptGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=50)
    style: str = Field(..., min_length=2, max_length=20)
    duration: int = Field(..., ge=1, le=60)  # in minutes

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=10)
    voice_id: str = Field(..., min_length=2, max_length=20)
    speed: float = Field(1.0, ge=0.5, le=2.0)

class ThumbnailRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    style: str = Field(..., min_length=2, max_length=20)
    colors: Optional[List[str]] = Field(None, max_items=5)

class ROICalculationRequest(BaseModel):
    views: int = Field(..., ge=0)
    cpm: float = Field(5.0, ge=0.1, le=100.0)

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str
