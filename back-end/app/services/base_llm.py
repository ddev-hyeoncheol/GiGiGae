from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseLLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str, schema: type[BaseModel]) -> Any:
        """LLM Prompt 전송 및 Pydantic 스키마 기반 Structured Output 반환"""
        ...
