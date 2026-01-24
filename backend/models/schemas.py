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
    format: Optional[str] = Field(None, max_length=10)

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

class CommerceJourneyEventCreate(BaseModel):
    stage: str = Field(..., min_length=2, max_length=50)
    channel: Optional[str] = Field(None, max_length=50)
    sku: Optional[str] = Field(None, max_length=64)
    metadata: Optional[Dict[str, Any]] = None

class CommerceJourneyEventResponse(BaseModel):
    id: int
    user_id: Optional[int]
    stage: str
    channel: Optional[str]
    sku: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class LoyaltyAwardRequest(BaseModel):
    user_id: Optional[int] = None
    points: int = Field(..., ge=1)
    reason: str = Field(..., min_length=2, max_length=120)
    reference: Optional[str] = Field(None, max_length=120)

class LoyaltyLedgerResponse(BaseModel):
    id: int
    delta: int
    reason: str
    reference: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class LoyaltyAccountResponse(BaseModel):
    user_id: int
    points_balance: int
    tier: str
    updated_at: Optional[datetime]
    ledger: List[LoyaltyLedgerResponse] = Field(default_factory=list)

class ContractCreate(BaseModel):
    org_name: str = Field(..., min_length=2, max_length=120)
    value: float = Field(..., ge=0)
    currency: str = Field("USD", min_length=3, max_length=10)
    status: str = Field("draft", min_length=2, max_length=40)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    terms: Optional[str] = None
    user_id: Optional[int] = None

class ContractResponse(BaseModel):
    id: int
    user_id: Optional[int]
    org_name: str
    status: str
    value: float
    currency: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    terms: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

class CommerceSummaryResponse(BaseModel):
    journey_events: int
    loyalty_points: int
    loyalty_tier: str
    active_contracts: int


class CommerceAssetResponse(BaseModel):
    id: int
    name: str
    file_path: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    checksum: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class OfferCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: float = Field(..., ge=0)
    currency: str = Field("USD", min_length=3, max_length=10)
    asset_id: Optional[int] = None
    offer_type: str = Field("printable", min_length=2, max_length=50)
    status: str = Field("active", min_length=2, max_length=40)
    sku: Optional[str] = Field(None, max_length=64)
    file_format: Optional[str] = Field(None, max_length=20)
    dimensions: Optional[str] = Field(None, max_length=50)
    dpi: Optional[int] = Field(None, ge=72, le=1200)
    license_terms: Optional[str] = Field(None, max_length=4000)
    tags: Optional[List[str]] = None


class OfferResponse(BaseModel):
    id: int
    sku: str
    title: str
    description: Optional[str]
    price: float
    currency: str
    status: str
    offer_type: str
    asset_id: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


class OfferCheckoutRequest(BaseModel):
    offer_id: Optional[int] = None
    sku: Optional[str] = Field(None, min_length=2, max_length=64)
    order_id: Optional[str] = Field(None, max_length=120)
    customer_email: Optional[str] = Field(None, max_length=200)
    customer_name: Optional[str] = Field(None, max_length=200)


class DeliveryResponse(BaseModel):
    id: int
    status: str
    method: str
    download_url: Optional[str]
    expires_at: Optional[datetime]
    delivered_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


class OrderResponse(BaseModel):
    order_id: str
    status: str
    amount: Optional[float]
    currency: Optional[str]
    paid_at: Optional[datetime]
    delivery: Optional[DeliveryResponse]

    model_config = {
        "from_attributes": True
    }


class DeliveryResendRequest(BaseModel):
    order_id: str = Field(..., min_length=4, max_length=120)
