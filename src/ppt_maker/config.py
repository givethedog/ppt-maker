"""설정 스키마 — TopicConfig, SectionConfig, SlideHint.

TOML 파일 또는 프로그래밍 방식으로 파이프라인 설정을 정의합니다.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from ppt_maker.errors import ConfigError, ConfigFileNotFoundError, ConfigValidationError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class SectionConfig:
    """보고서 섹션 하나의 설정."""

    title: str
    content: str = ""
    slide_type: str = "auto"
    conversion_strategy: str = "auto"

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ConfigValidationError("title", "섹션 제목은 비어 있을 수 없습니다.")
        valid_strategies = {"auto", "pandoc", "custom"}
        if self.conversion_strategy not in valid_strategies:
            raise ConfigValidationError(
                "conversion_strategy",
                f"허용 값: {', '.join(sorted(valid_strategies))}",
            )


@dataclass
class SlideHint:
    """마크다운 내 슬라이드 변환 힌트."""

    section_index: int
    slide_type: str
    conversion_strategy: str = "auto"
    extra: dict = field(default_factory=dict)


@dataclass
class TopicConfig:
    """파이프라인 전체 설정."""

    topic: str
    subtitle: str = ""
    author: str = ""
    date: str = ""
    sections: list[SectionConfig] = field(default_factory=list)
    theme: str = "default"
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    font_family: str = "auto"
    slide_width: float = 13.333
    slide_height: float = 7.5

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ConfigValidationError("topic", "주제는 비어 있을 수 없습니다.")
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if self.slide_width <= 0 or self.slide_height <= 0:
            raise ConfigValidationError(
                "slide_width/slide_height", "슬라이드 크기는 양수여야 합니다."
            )

    @classmethod
    def from_toml(cls, path: Path) -> TopicConfig:
        """TOML 파일에서 설정을 로드합니다."""
        path = Path(path)
        if not path.exists():
            raise ConfigFileNotFoundError(str(path))

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            raise ConfigError(
                f"TOML 파일 파싱 실패: {path}",
                detail=str(e),
            ) from e

        project = data.get("project", data)

        sections_raw = project.pop("sections", [])
        sections = [
            SectionConfig(**s) if isinstance(s, dict) else s
            for s in sections_raw
        ]

        try:
            return cls(sections=sections, **project)
        except TypeError as e:
            raise ConfigError(
                f"설정 파일에 잘못된 필드가 있습니다: {path}",
                detail=str(e),
            ) from e
