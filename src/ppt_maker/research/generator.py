"""콘텐츠 생성기 — 주제에서 섹션 콘텐츠 자동 생성."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from rich.console import Console

from ppt_maker.config import SectionConfig
from ppt_maker.research.llm import LLMClient, LLMConfig

console = Console()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """당신은 전문 보고서 작성 AI입니다.
주어진 주제에 대해 프레젠테이션용 섹션 콘텐츠를 생성합니다.

응답 형식 (JSON):
{
  "sections": [
    {
      "title": "섹션 제목",
      "content": "마크다운 형식의 섹션 내용 (bullet points 포함)",
      "slide_type": "content"
    }
  ]
}

slide_type 옵션: title, section, content, comparison, timeline, quote, keynote
- title: 표지 슬라이드 (첫 번째 섹션)
- section: 구분 슬라이드
- content: 일반 내용 슬라이드
- comparison: 비교 슬라이드
- timeline: 타임라인 슬라이드
- quote: 인용 슬라이드
- keynote: 핵심 요약 슬라이드 (마지막 섹션)
"""


@dataclass
class GeneratedContent:
    """생성된 콘텐츠 결과."""

    sections: list[SectionConfig] = field(default_factory=list)
    raw_response: str = ""


class ContentGenerator:
    """LLM을 사용한 콘텐츠 생성기."""

    def __init__(self, llm_config: LLMConfig | None = None) -> None:
        self._config = llm_config or LLMConfig()
        self._client: LLMClient | None = None

    def _get_client(self) -> LLMClient:
        if self._client is None:
            self._client = LLMClient(self._config)
        return self._client

    def generate(self, topic: str, subtitle: str = "", num_slides: int = 8) -> GeneratedContent:
        """주제에 대한 섹션 콘텐츠를 생성."""
        client = self._get_client()

        user_prompt = f"주제: {topic}"
        if subtitle:
            user_prompt += f"\n부제: {subtitle}"
        user_prompt += f"\n\n{num_slides}개의 슬라이드로 구성된 프레젠테이션 콘텐츠를 생성해주세요."

        raw = client.chat(SYSTEM_PROMPT, user_prompt)
        result = GeneratedContent(raw_response=raw)

        # JSON 파싱
        try:
            # ```json ... ``` 블록 처리
            text = raw.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                # 외부 래퍼만 제거 (첫 줄 ```json, 마지막 줄 ```)
                if lines and lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text = "\n".join(lines)

            data = json.loads(text)
            sections_data = data.get("sections", [])

            for s in sections_data:
                result.sections.append(
                    SectionConfig(
                        title=s.get("title", "제목 없음"),
                        content=s.get("content", ""),
                        slide_type=s.get("slide_type", "content"),
                    )
                )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("LLM 응답 파싱 실패, 원본 텍스트를 단일 섹션으로 사용: %s", e)
            console.print(
                "[yellow]LLM 응답 파싱 실패 — 원본 텍스트를 단일 섹션으로 사용합니다.[/]"
            )
            result.sections.append(
                SectionConfig(
                    title=topic,
                    content=raw,
                    slide_type="content",
                )
            )

        logger.info("콘텐츠 생성 완료: %d개 섹션", len(result.sections))
        return result
