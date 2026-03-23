"""GiGiGae FastAPI 앱 진입점"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.constants import API_V1_PREFIX
from app.core.database import close_pool, get_pool, init_pool
from app.core.exceptions import AppException, app_exception_handler
from app.plugins.ollama_plugin import OllamaPlugin
from app.utils.logger import get_logger

logger = get_logger(__name__)

app_state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 플러그인 초기화 및 정리"""
    logger.info("Initializing plugins...")

    app_state["llm"] = OllamaPlugin()

    await init_pool()

    logger.info(f"LLM: OllamaPlugin (model={settings.ollama_model})")
    logger.info(f"Trademark DB: {'연결됨' if get_pool() else 'Mock 모드'}")

    yield

    await close_pool()
    app_state.clear()
    logger.info("Plugins shut down.")


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

app.include_router(api_router, prefix=API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok"}
