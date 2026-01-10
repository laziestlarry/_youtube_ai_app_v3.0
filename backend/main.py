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
from backend.core import database as db
from backend.core.seed_db import seed_db
from backend.services.bizop_service import BizOpportunityService

# Import routers with absolute imports
from backend.api.dashboard import router as dashboard_router
from backend.api.routes.auth import router as auth_router
from backend.models.user import User # Register User model
from backend.models.youtube import ChannelStats, VideoAnalytics # Register YouTube models
from backend.models.content import ContentIdea # Register Content models
from backend.models.workflow import WorkflowColumn, WorkflowCard # Register Workflow models
from backend.models.bizop import BizOpportunity # Register BizOpportunity models
from backend.models.revenue import RevenueEvent # Register Revenue models

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
        await db.init_db()
        await seed_db() # Seed with default data
        logger.info("Database initialized and seeded successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue startup even if database fails

    try:
        auto_sync = os.getenv("BIZOP_AUTO_SYNC", "true").lower() in ("1", "true", "yes")
        if auto_sync:
            if db.AsyncSessionLocal is None:
                db.create_database_engines()
            async with db.AsyncSessionLocal() as session:
                result = await BizOpportunityService().sync_from_sources(session=session)
                logger.info("BizOp sync completed: %s", result)
    except Exception as e:
        logger.warning("BizOp sync failed: %s", e)
    
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
def normalize_cors_origins(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(origin).strip() for origin in value if str(origin).strip()]
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        if raw == "*":
            return ["*"]
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = None
        if isinstance(parsed, list):
            return [str(origin).strip() for origin in parsed if str(origin).strip()]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return []

local_origins = [
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

configured_origins = normalize_cors_origins(getattr(settings, "cors_origins", None))
environment = str(getattr(settings, "environment", "")).lower()

if environment == "production":
    if configured_origins and configured_origins != ["*"]:
        origins = configured_origins
    else:
        fallback_origin = getattr(settings, "frontend_origin", None)
        origins = [fallback_origin] if fallback_origin else []
else:
    origins = list(local_origins)
    if configured_origins == ["*"]:
        origins = ["*"]
    else:
        for origin in configured_origins:
            if origin not in origins:
                origins.append(origin)

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
from backend.api.routes.agency import router as agency_router
app.include_router(workflow_router, prefix="/api/workflow", tags=["workflow"])
app.include_router(agency_router, prefix="/api/agency", tags=["agency"])
from backend.api.routes.payment import router as payment_router
app.include_router(payment_router, prefix="/api/payment", tags=["payment"])
from backend.api.routes.ai import router as ai_router
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
from backend.api.routes.bizop import router as bizop_router
app.include_router(bizop_router, prefix="/api/bizop", tags=["bizop"])
from backend.api.routes.looker_actions import router as looker_router
app.include_router(looker_router, prefix="/api/looker", tags=["looker"])
from backend.api.routes.kpi import router as kpi_router
app.include_router(kpi_router, prefix="/api/kpi", tags=["kpi"])
from backend.api.routes.outcomes import router as outcomes_router
app.include_router(outcomes_router, prefix="/api/outcomes", tags=["outcomes"])
from backend.api.routes.growth import router as growth_router
app.include_router(growth_router, prefix="/api/growth", tags=["growth"])

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

# Check if Next.js Export exists and mount it
try:
    frontend_build_path = Path("frontend/dist")
    next_static_path = Path("frontend/dist/_next")
    
    if next_static_path.exists():
        # Mount /_next/static to frontend/dist/_next/static
        app.mount("/_next", StaticFiles(directory="frontend/dist/_next"), name="next_static")
        logger.info("✅ Next.js static assets mounted at /_next")
    else:
        logger.info("ℹ️  Next.js _next directory not found in frontend/dist")
        
    if frontend_build_path.exists():
        logger.info("✅ Frontend build found")
    else:
        logger.info("ℹ️  Frontend build not found - run 'npm install && npm run build' in frontend directory")
        
except Exception as e:
    logger.warning(f"Could not mount Frontend assets: {e}")

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
    db_health = await db.check_db_health()
    
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
    if getattr(settings, "shopier_app_mode", False):
        shopier_store = Path("static/store.html")
        if shopier_store.exists():
            return FileResponse(shopier_store)

    # Check if React build exists
    frontend_build_path = Path("frontend/dist")
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
        full_path.startswith("assets/") or
        full_path.startswith("_next/")):
        raise HTTPException(status_code=404, detail="Endpoint not found")

    if getattr(settings, "shopier_app_mode", False):
        shopier_store = Path("static/store.html")
        if shopier_store.exists():
            return FileResponse(shopier_store)
    
    # Check if React build exists
    frontend_build_path = Path("frontend/dist")
    if frontend_build_path.exists():
        # 1. Check for specific HTML file (e.g. /opportunities -> opportunities.html)
        html_file = frontend_build_path / f"{full_path}.html"
        if html_file.exists():
             return FileResponse(html_file)
        
        # 2. Check for directory index (e.g. /opportunities -> opportunities/index.html)
        dir_index = frontend_build_path / full_path / "index.html"
        if dir_index.exists():
            return FileResponse(dir_index)

        # 3. Fallback to main index.html (SPA routing)
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
