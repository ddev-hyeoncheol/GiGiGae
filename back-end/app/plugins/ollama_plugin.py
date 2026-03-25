"""Ollama LLM API 플러그인"""

from typing import Any

import httpx
import ollama
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import LLMGenerationError, LLMTimeoutError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaPlugin:
    """Ollama LLM API 클라이언트"""

    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or settings.ollama_model
        self.client = ollama.AsyncClient(
            host=base_url or settings.ollama_base_url,
            timeout=httpx.Timeout(settings.ollama_timeout),
        )

    async def generate(
        self, prompt: str, system_prompt: str, schema: type[BaseModel]
    ) -> Any:
        """Ollama API를 통한 Pydantic 스키마 기반 Structured Output 반환"""
        try:
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                format=schema.model_json_schema(),
                think=False,
                options={
                    "temperature": 0.75,
                    "num_predict": 1024,
                    "num_ctx": 2048,
                    "top_k": 50,
                    "top_p": 0.9,
                },
            )
            return schema.model_validate_json(response["message"]["content"])
        except (TimeoutError, httpx.TimeoutException) as e:
            logger.error(f"[LLM Timeout] {e}")
            raise LLMTimeoutError(detail=str(e))
        except Exception as e:
            logger.error(f"[LLM Error] {type(e).__name__}: {e}")
            raise LLMGenerationError(detail=str(e))
