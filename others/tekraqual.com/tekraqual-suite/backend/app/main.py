from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.seed import ensure_seed_data
from app.db.session import Base, engine


app = FastAPI(title=settings.PROJECT_NAME)

if settings.AUTO_CREATE_TABLES:
    Base.metadata.create_all(bind=engine)
    ensure_seed_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
