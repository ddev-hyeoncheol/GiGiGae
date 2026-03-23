"""API 라우터 통합 모듈"""

from fastapi import APIRouter

from app.api import recommend, trademark

api_router = APIRouter()

api_router.include_router(recommend.router)
api_router.include_router(trademark.router)
