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

OUTLINE_SYSTEM_PROMPT = """당신은 전문 보고서 작성 AI입니다.
주어진 주제와 섹션 목차에 따라 각 섹션의 상세 콘텐츠를 생성합니다.

대상, 목적, 톤에 맞게 콘텐츠를 조정하세요:
- executive (임원진): 핵심 요약 위주, 수치와 결론 중심
- team (팀원): 기술 상세, 구현 방안 중심
- general (전사): 쉬운 설명, 사례 중심

응답 형식 (JSON):
{
  "sections": [
    {
      "title": "섹션 제목",
      "content": "마크다운 형식의 상세 내용 (bullet points, 수치 포함)",
      "slide_type": "content"
    }
  ]
}

slide_type 옵션: title, section, content, comparison, timeline, quote, keynote
"""

REGENERATE_SYSTEM_PROMPT = """당신은 전문 보고서 작성 AI입니다.
기존 프레젠테이션의 한 섹션을 사용자 요청에 따라 재작성합니다.

전체 맥락을 고려하되, 요청된 섹션만 수정하세요.
다른 섹션의 내용은 참고만 하고 변경하지 마세요.

응답: 수정된 섹션의 content만 마크다운으로 출력하세요.
JSON이 아닌 순수 마크다운 텍스트로 응답하세요.
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

    def _parse_sections(self, raw: str, fallback_topic: str) -> list[SectionConfig]:
        """LLM JSON 응답을 SectionConfig 리스트로 파싱.

        파싱 실패 시 원본 텍스트를 단일 섹션으로 반환.
        """
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

            return [
                SectionConfig(
                    title=s.get("title", "제목 없음"),
                    content=s.get("content", ""),
                    slide_type=s.get("slide_type", "content"),
                )
                for s in sections_data
            ]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("LLM 응답 파싱 실패, 원본 텍스트를 단일 섹션으로 사용: %s", e)
            console.print(
                "[yellow]LLM 응답 파싱 실패 — 원본 텍스트를 단일 섹션으로 사용합니다.[/]"
            )
            return [SectionConfig(title=fallback_topic, content=raw, slide_type="content")]

    def generate(self, topic: str, subtitle: str = "", num_slides: int = 8) -> GeneratedContent:
        """주제에 대한 섹션 콘텐츠를 생성."""
        client = self._get_client()

        user_prompt = f"주제: {topic}"
        if subtitle:
            user_prompt += f"\n부제: {subtitle}"
        user_prompt += f"\n\n{num_slides}개의 슬라이드로 구성된 프레젠테이션 콘텐츠를 생성해주세요."

        raw = client.chat(SYSTEM_PROMPT, user_prompt)
        result = GeneratedContent(raw_response=raw)
        result.sections = self._parse_sections(raw, topic)

        logger.info("콘텐츠 생성 완료: %d개 섹션", len(result.sections))
        return result

    def generate_with_outline(
        self,
        topic: str,
        subtitle: str = "",
        outline: list[str] | None = None,
        audience: str = "team",
        purpose: str = "report",
        tone: str = "professional",
    ) -> GeneratedContent:
        """목차 기반 상세 콘텐츠 생성."""
        client = self._get_client()

        user_prompt = f"주제: {topic}"
        if subtitle:
            user_prompt += f"\n부제: {subtitle}"
        user_prompt += f"\n대상: {audience}\n목적: {purpose}\n톤: {tone}"

        if outline:
            user_prompt += "\n\n섹션 목차:\n"
            user_prompt += "\n".join(f"{i+1}. {title}" for i, title in enumerate(outline))

        user_prompt += "\n\n위 목차에 따라 각 섹션의 상세 콘텐츠를 생성해주세요."

        raw = client.chat(OUTLINE_SYSTEM_PROMPT, user_prompt)
        result = GeneratedContent(raw_response=raw)
        result.sections = self._parse_sections(raw, topic)

        logger.info("목차 기반 콘텐츠 생성 완료: %d개 섹션", len(result.sections))
        return result

    def regenerate_section(
        self,
        all_sections: list[SectionConfig],
        section_index: int,
        instruction: str,
        topic: str,
    ) -> str:
        """특정 섹션을 사용자 지시에 따라 재생성.

        Args:
            all_sections: 전체 섹션 리스트 (맥락용).
            section_index: 재생성할 섹션 인덱스.
            instruction: 사용자의 수정 요청.
            topic: 전체 주제.

        Returns:
            재생성된 섹션 content (마크다운 텍스트).
        """
        client = self._get_client()

        # 전체 목차를 맥락으로 제공
        outline = "\n".join(
            f"{i+1}. [{s.slide_type}] {s.title}"
            for i, s in enumerate(all_sections)
        )
        target = all_sections[section_index]

        user_prompt = (
            f"주제: {topic}\n\n"
            f"전체 목차:\n{outline}\n\n"
            f"수정 대상: {section_index + 1}. {target.title}\n"
            f"현재 내용:\n{target.content}\n\n"
            f"수정 요청: {instruction}\n\n"
            f"위 섹션의 수정된 내용을 마크다운으로 작성해주세요."
        )

        return client.chat(REGENERATE_SYSTEM_PROMPT, user_prompt)
