from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime
from simple_youtube_optimizer import quick_income_strategy, SimpleYouTubeOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Income Commander",
    description="Generate YouTube income fast with AI-powered content ideas",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global optimizer instance
optimizer = SimpleYouTubeOptimizer()

@app.get("/")
async def root():
    return {
        "message": "YouTube Income Commander - Ready to Generate Revenue",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test core functionality
        test_ideas = optimizer.generate_money_making_ideas(1)
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "core_function": "operational" if test_ideas else "degraded"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/quick-strategy")
async def get_quick_strategy():
    """Get immediate income generation strategy"""
    try:
        strategy = quick_income_strategy()
        logger.info("Quick strategy generated successfully")
        return strategy
    except Exception as e:
        logger.error(f"Error generating quick strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/money-ideas")
async def get_money_ideas(count: int = 5):
    """Get money-making video ideas"""
    try:
        if count > 20:  # Rate limiting
            count = 20
        
        ideas = optimizer.generate_money_making_ideas(count)
        total_revenue = sum(idea["estimated_revenue"] for idea in ideas)
        
        logger.info(f"Generated {len(ideas)} money ideas, total revenue potential: ${total_revenue}")
        
        return {
            "ideas": ideas,
            "total_revenue_potential": round(total_revenue, 2),
            "generated_at": datetime.utcnow().isoformat(),
            "count": len(ideas)
        }
    except Exception as e:
        logger.error(f"Error generating money ideas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint for monitoring"""
    return {
        "app_name": "YouTube Income Commander",
        "version": "1.0.0",
        "uptime": "operational",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        workers=2 if os.getenv("ENVIRONMENT") == "production" else 1
    )