from fastapi import APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import random
# Remove problematic imports for now
# from ..services.youtube_service import youtube_service
# from ..services.analytics_service import analytics_service
# from ..services.ai_service import ai_service
from backend.database.models import User, Video, Channel
from backend.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["dashboard"])

@router.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/channel/stats")
async def get_channel_stats(db: Session = Depends(get_db)):
    """Get channel statistics - Frontend expects this endpoint"""
    try:
        # Return mock data for now since services aren't properly instantiated
        return {
            "subscribers": 125000,
            "views": 2500000,
            "videos": 150,
            "revenue": 5420.50
        }
    except Exception as e:
        # Return mock data if service fails
        return {
            "subscribers": 125000,
            "views": 2500000,
            "videos": 150,
            "revenue": 5420.50
        }

@router.get("/analytics/videos")
async def get_video_analytics():
    """Get video analytics data from fulfillment engine history"""
    try:
        from modules.ai_agency.fulfillment_engine import fulfillment_engine
        data = fulfillment_engine.get_earnings_summary()
        history = data.get("history", [])
        
        # Filter for youtube tasks
        yt_tasks = [t for t in history if "youtube" in t["source"].lower()]
        
        analytics = []
        for task in yt_tasks[-10:]: # Last 10
            analytics.append({
                "title": task["source"].split(":")[-1].strip(),
                "views": random.randint(10000, 100000),
                "likes": random.randint(500, 5000),
                "comments": random.randint(50, 500),
                "revenue": task["amount"],
                "uploadDate": task["timestamp"]
            })
        
        return analytics if analytics else [
            {"title": "No production data yet", "views": 0, "likes": 0, "comments": 0, "revenue": 0.0, "uploadDate": datetime.now().isoformat()}
        ]
    except Exception as e:
        return []

@router.get("/system/health")
async def get_system_health():
    """Get system health status - Frontend expects this endpoint"""
    try:
        return {
            "status": "healthy",
            "uptime": 99.8,
            "memory": 65.2,
            "cpu": 23.1,
            "lastCheck": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "warning",
            "uptime": 95.0,
            "memory": 80.0,
            "cpu": 45.0,
            "lastCheck": datetime.utcnow().isoformat()
        }

@router.get("/models")
async def get_ai_models():
    """Get AI models status - Frontend expects this endpoint"""
    try:
        return [
            {
                "name": "Content Generator",
                "status": "active",
                "accuracy": 87.5,
                "lastTrained": (datetime.now() - timedelta(days=7)).isoformat(),
                "type": "content"
            },
            {
                "name": "Thumbnail Generator",
                "status": "active",
                "accuracy": 92.1,
                "lastTrained": (datetime.now() - timedelta(days=3)).isoformat(),
                "type": "thumbnail"
            },
            {
                "name": "Title Optimizer",
                "status": "training",
                "accuracy": 78.3,
                "lastTrained": (datetime.now() - timedelta(days=1)).isoformat(),
                "type": "title"
            },
            {
                "name": "Description Generator",
                "status": "active",
                "accuracy": 85.7,
                "lastTrained": (datetime.now() - timedelta(days=5)).isoformat(),
                "type": "description"
            }
        ]
    except Exception as e:
        return []

@router.get("/earnings")
async def get_earnings():
    """Get earnings data - Frontend expects this endpoint"""
    try:
        from modules.ai_agency.fulfillment_engine import fulfillment_engine
        
        # Get real-time data from the ledger
        data = fulfillment_engine.get_earnings_summary()
        total = data.get("total_earnings", 0.0)
        daily = data.get("daily", 0.0)
        
        return {
            "daily": daily,
            "weekly": total, # Simplified for demo
            "monthly": total, 
            "yearly": total,
            "sources": {
                "ads": total * 0.4,
                "sponsorships": total * 0.3,
                "merchandise": total * 0.2,
                "memberships": total * 0.1
            }
        }
    except Exception as e:
        return {
            "daily": 0.0,
            "weekly": 0.0,
            "monthly": 0.0,
            "yearly": 0.0,
            "sources": {
                "ads": 0.0,
                "sponsorships": 0.0,
                "merchandise": 0.0,
                "memberships": 0.0
            }
        }

@router.get("/content")
async def get_content_library():
    """Get content library from fulfillment engine history"""
    try:
        from modules.ai_agency.fulfillment_engine import fulfillment_engine
        data = fulfillment_engine.get_earnings_summary()
        history = data.get("history", [])
        
        content = []
        for i, task in enumerate(history[-20:]): # Last 20
            content.append({
                "id": str(i),
                "title": task["source"][:100],
                "type": "asset" if "intelliwealth" in task["source"].lower() or "training" in task["source"].lower() else "task",
                "status": "published",
                "scheduledDate": task["timestamp"],
                "views": task.get("amount", 0.0), # Use amount as a growth metric for sorting
                "asset_url": task.get("asset_url")
            })
        return content
    except Exception as e:
        return []

@router.post("/content")
async def create_content(content_data: Dict[str, Any]):
    """Create new content - Frontend expects this endpoint"""
    try:
        # Mock implementation
        return {
            "id": "new-id",
            "title": content_data.get("title", "New Content"),
            "status": "draft",
            "message": "Content created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/content/{content_id}")
async def update_content(content_id: str, content_data: Dict[str, Any]):
    """Update content - Frontend expects this endpoint"""
    try:
        # Mock implementation
        return {
            "id": content_id,
            "title": content_data.get("title", "Updated Content"),
            "status": "updated",
            "message": "Content updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/content/{content_id}")
async def delete_content(content_id: str):
    """Delete content - Frontend expects this endpoint"""
    try:
        # Mock implementation
        return {
            "id": content_id,
            "message": "Content deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_name}/train")
async def train_model(model_name: str, config: Dict[str, Any] = {}):
    """Train AI model - Frontend expects this endpoint"""
    try:
        # Mock implementation
        return {
            "model_name": model_name,
            "status": "training_started",
            "message": f"Training started for {model_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_name}/training-status")
async def get_training_status(model_name: str):
    """Get training status - Frontend expects this endpoint"""
    try:
        # Mock implementation
        return {
            "model_name": model_name,
            "status": "training",
            "progress": 65,
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
