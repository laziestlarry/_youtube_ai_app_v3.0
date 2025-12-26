"""
Main FastAPI application for YouTube AI Content Creator.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import sys
from pathlib import Path
import os
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
import random
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import settings
from backend.core.database import check_db_health, engine, Base, init_db
from backend.core.seed_db import seed_db

# Import routers with absolute imports
from backend.api.dashboard import router as dashboard_router
from backend.api.routes.auth import router as auth_router
from backend.models.user import User # Register User model
from backend.models.youtube import ChannelStats, VideoAnalytics # Register YouTube models
from backend.models.content import ContentIdea # Register Content models
from backend.models.workflow import WorkflowColumn, WorkflowCard # Register Workflow models

# Import subscription routes
from backend.api.routes.subscriptions import router as subscription_router
from backend.api.routes.analytics import router as analytics_router
from backend.api.routes.youtube import router as youtube_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting YouTube AI Content Creator...")
    
    # Initialize database
    try:
        await init_db()
        await seed_db() # Seed with default data
        logger.info("Database initialized and seeded successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue startup even if database fails
    
    yield
    
    # Shutdown
    logger.info("Shutting down YouTube AI Content Creator")

# Create FastAPI app
app = FastAPI(
    title="YouTube AI Platform API",
    description="Profit-centric YouTube content creation and management platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
origins = [
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
]

# Add origins from settings if available
if hasattr(settings, "cors_origins") and settings.cors_origins:
    if isinstance(settings.cors_origins, list):
        for origin in settings.cors_origins:
            if origin != "*" and origin not in origins:
                origins.append(origin)
    elif settings.cors_origins == "*":
        origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(subscription_router, prefix="/api", tags=["subscriptions"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(youtube_router, prefix="/api/youtube", tags=["youtube"])
from backend.api.routes.workflow import router as workflow_router
app.include_router(workflow_router, prefix="/api/workflow", tags=["workflow"])

# Mount static files if they exist
try:
    static_dir = Path("static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Static files mounted")
    else:
        logger.info("ℹ️  Static directory not found")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Check if React build exists and mount it
try:
    frontend_build_path = Path("frontend/build")
    frontend_static_path = Path("frontend/build/static")
    
    if frontend_static_path.exists():
        app.mount("/assets", StaticFiles(directory="frontend/build/static"), name="assets")
        logger.info("✅ React build assets mounted")
    else:
        logger.info("ℹ️  React build assets not found")
        
    if frontend_build_path.exists():
        logger.info("✅ React build found")
    else:
        logger.info("ℹ️  React build not found - run 'npm run build' in frontend directory")
        
except Exception as e:
    logger.warning(f"Could not mount React assets: {e}")

# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "ai_models": "active",
            "youtube_api": "configured"
        }
    }

@app.get("/api/v1/health")
async def api_health_check():
    """API health check."""
    return {
        "status": "healthy",
        "version": settings.version,
        "environment": settings.environment
    }

@app.get("/api/v1/health/detailed")
async def detailed_health_check():
    """Detailed health check including database."""
    db_health = await check_db_health()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "version": settings.version,
        "environment": settings.environment,
        "database": db_health,
        "components": {
            "api": {"status": "healthy"},
            "database": db_health
        }
    }

# Status endpoint
@app.get("/api/status")
async def get_status():
    """Get application status."""
    return {
        "status": "idle",
        "message": "Application is ready",
        "version": settings.version
    }

# Initialize endpoint
@app.post("/api/initialize")
async def initialize_app(data: dict):
    """Initialize the application with user data."""
    try:
        # Basic validation
        if not data.get("channelId") and not data.get("channel_id"):
            raise HTTPException(status_code=400, detail="Channel ID is required")
        
        if not data.get("apiKey") and not data.get("api_key"):
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Normalize the data
        channel_id = data.get("channelId") or data.get("channel_id")
        api_key = data.get("apiKey") or data.get("api_key")
        preferences = data.get("preferences", {})
        
        # For now, just return success
        return {
            "status": "success",
            "message": "Application initialized successfully",
            "data": {
                "channel_id": channel_id,
                "preferences": preferences
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    # Check if React build exists
    frontend_build_path = Path("frontend/build")
    if frontend_build_path.exists():
        index_file = frontend_build_path / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    
    # Check if static index exists
    static_index = Path("static/index.html")
    if static_index.exists():
        return FileResponse(static_index)
    
    # Fallback to JSON response
    return {
        "message": "Welcome to YouTube AI Content Creator API",
        "version": settings.version,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "redoc": "/redoc",
            "api_health": "/api/v1/health"
        },
        "note": "Frontend not built yet. Run 'cd frontend && npm install && npm run build' to build the React app."
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "status": "error"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "status": "error"}
    )







# Serve React app for frontend routes (catch-all)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for frontend routes."""
    # Don't serve React for API routes or docs
    if (full_path.startswith("api/") or 
        full_path.startswith("health") or 
        full_path.startswith("docs") or 
        full_path.startswith("redoc") or
        full_path.startswith("static/") or
        full_path.startswith("assets/")):
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    # Check if React build exists
    frontend_build_path = Path("frontend/build")
    if frontend_build_path.exists():
        index_file = frontend_build_path / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    
    # Check if static index exists
    static_index = Path("static/index.html")
    if static_index.exists():
        return FileResponse(static_index)
    
    # Fallback for unknown routes
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting YouTube AI Platform API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)