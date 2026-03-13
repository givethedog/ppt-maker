"""LLM 클라이언트 — OpenAI 호환 API 래퍼."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from openai import OpenAI

from ppt_maker.errors import PptMakerError

logger = logging.getLogger(__name__)


class LLMError(PptMakerError):
    """LLM API 호출 관련 오류."""


@dataclass(frozen=True)
class LLMConfig:
    """LLM API 설정."""

    api_base: str = ""
    model: str = "gpt-4o-mini"
    api_key_env: str = "LLM_API_KEY"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0


class LLMClient:
    """OpenAI 호환 API 클라이언트."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._client = self._build_client()

    def _build_client(self):
        """openai.OpenAI 클라이언트 생성."""
        api_key = os.environ.get(self.config.api_key_env, "")
        if not api_key:
            raise LLMError(
                "API 키가 설정되지 않았습니다.",
                detail=f"환경변수 {self.config.api_key_env} 를 설정하세요.",
            )
        kwargs: dict = {"api_key": api_key}
        if self.config.api_base:
            kwargs["base_url"] = self.config.api_base
        return OpenAI(**kwargs)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """채팅 완성 API 호출."""
        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
            )
            content = response.choices[0].message.content
            if content is None:
                raise LLMError("LLM 응답이 비어 있습니다.")
            return content.strip()
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(
                f"LLM API 호출 실패: {e}",
            ) from e
