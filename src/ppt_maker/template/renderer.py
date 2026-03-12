"""Jinja2 렌더러 — 마크다운 보고서 생성."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
)
from jinja2 import (
    TemplateError as JinjaTemplateError,
)

from ppt_maker.config import SlideHint, TopicConfig
from ppt_maker.errors import TemplateError
from ppt_maker.template.filters import CUSTOM_FILTERS

logger = logging.getLogger(__name__)

BUILTIN_TEMPLATES_DIR = Path(__file__).parent / "templates"

# 슬라이드 힌트 주석 패턴: <!-- slide: type=timeline, strategy=custom -->
HINT_PATTERN = re.compile(
    r"<!--\s*slide:\s*(.*?)\s*-->",
    re.IGNORECASE,
)


@dataclass
class RenderedReport:
    """렌더링 결과."""

    markdown: str
    slide_hints: list[SlideHint] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def _parse_hints(markdown: str) -> list[SlideHint]:
    """마크다운에서 슬라이드 힌트 주석을 파싱."""
    hints = []
    section_index = 0

    for line in markdown.split("\n"):
        if line.startswith("## "):
            section_index += 1

        match = HINT_PATTERN.search(line)
        if match:
            attrs_str = match.group(1)
            attrs: dict[str, str] = {}
            for pair in attrs_str.split(","):
                pair = pair.strip()
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    attrs[k.strip()] = v.strip()

            hints.append(SlideHint(
                section_index=section_index,
                slide_type=attrs.get("type", "content"),
                conversion_strategy=attrs.get("strategy", "auto"),
                extra={k: v for k, v in attrs.items() if k not in ("type", "strategy")},
            ))

    return hints


class TemplateRenderer:
    """Jinja2 기반 마크다운 렌더러."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        search_dirs = []
        if templates_dir:
            search_dirs.append(str(templates_dir))
        search_dirs.append(str(BUILTIN_TEMPLATES_DIR))

        self._env = Environment(
            loader=FileSystemLoader(search_dirs),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters.update(CUSTOM_FILTERS)

    def render(self, template_name: str, config: TopicConfig) -> RenderedReport:
        """템플릿을 렌더링하여 마크다운 보고서를 생성."""
        try:
            template = self._env.get_template(template_name)
        except JinjaTemplateError as e:
            raise TemplateError(
                f"템플릿을 찾을 수 없습니다: {template_name}",
                detail=str(e),
            ) from e

        context = {
            "topic": config.topic,
            "subtitle": config.subtitle,
            "author": config.author,
            "date": config.date,
            "sections": config.sections,
            "theme": config.theme,
        }

        try:
            markdown = template.render(**context)
        except JinjaTemplateError as e:
            raise TemplateError(
                f"템플릿 렌더링 실패: {template_name}",
                detail=str(e),
            ) from e

        hints = _parse_hints(markdown)

        return RenderedReport(
            markdown=markdown,
            slide_hints=hints,
            metadata={
                "title": config.topic,
                "subtitle": config.subtitle,
                "section_count": len(config.sections),
                "hint_count": len(hints),
            },
        )

    def render_string(self, template_str: str, config: TopicConfig) -> RenderedReport:
        """문자열 템플릿을 렌더링."""
        try:
            template = self._env.from_string(template_str)
        except JinjaTemplateError as e:
            raise TemplateError("템플릿 문자열 파싱 실패", detail=str(e)) from e

        context = {
            "topic": config.topic,
            "subtitle": config.subtitle,
            "author": config.author,
            "date": config.date,
            "sections": config.sections,
            "theme": config.theme,
        }

        try:
            markdown = template.render(**context)
        except JinjaTemplateError as e:
            raise TemplateError("템플릿 문자열 렌더링 실패", detail=str(e)) from e

        hints = _parse_hints(markdown)
        return RenderedReport(
            markdown=markdown,
            slide_hints=hints,
            metadata={
                "title": config.topic,
                "section_count": len(config.sections),
                "hint_count": len(hints),
            },
        )
