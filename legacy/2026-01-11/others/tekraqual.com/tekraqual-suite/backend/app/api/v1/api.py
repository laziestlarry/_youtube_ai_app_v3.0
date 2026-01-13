from fastapi import APIRouter

from app.api.v1 import routes_assessments


api_router = APIRouter()
api_router.include_router(routes_assessments.router)
