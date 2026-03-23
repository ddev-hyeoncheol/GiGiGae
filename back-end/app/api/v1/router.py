from fastapi import APIRouter

from app.api.v1.endpoints import recommend

v1_router = APIRouter()

v1_router.include_router(recommend.router)
