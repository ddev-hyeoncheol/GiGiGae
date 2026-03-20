from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.constants import API_V1_PREFIX
from app.core.exceptions import AppException, app_exception_handler
from app.services.mock_image import MockImageService
from app.services.ollama_service import OllamaService
from app.utils.logger import get_logger

logger = get_logger(__name__)

app_state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 서비스 초기화 및 정리"""
    logger.info("Initializing services...")

    app_state["llm_service"] = OllamaService()
    app_state["image_service"] = MockImageService()

    logger.info(f"LLM: OllamaService (model={settings.ollama_model})")
    logger.info("Image: MockImageService")
    logger.info(f"Domain mock mode: {settings.use_mock_domain}")

    yield

    app_state.clear()
    logger.info("Services shut down.")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(v1_router, prefix=API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok"}
