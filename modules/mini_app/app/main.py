from fastapi import FastAPI
from .routers import commander_api
from .config import settings
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Income Commander Mini",
    description="MVP for rapid commercial outcome YouTube idea generation and main platform initiation.",
    version="0.1.0"
)

app.include_router(commander_api.router, prefix="/api/mini/v1")

@app.get("/")
async def root():
    return {"message": "YouTube Income Commander Mini is operational!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)