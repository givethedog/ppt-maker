"""config.py 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from ppt_maker.config import SectionConfig, SlideHint, TopicConfig
from ppt_maker.errors import ConfigFileNotFoundError, ConfigValidationError


class TestTopicConfig:
    def test_create_with_defaults(self) -> None:
        cfg = TopicConfig(topic="테스트 주제")
        assert cfg.topic == "테스트 주제"
        assert cfg.theme == "default"
        assert cfg.font_family == "auto"
        assert cfg.sections == []
        assert cfg.slide_width == 13.333

    def test_empty_topic_raises(self) -> None:
        with pytest.raises(ConfigValidationError, match="주제는 비어 있을 수 없습니다"):
            TopicConfig(topic="")

    def test_whitespace_topic_raises(self) -> None:
        with pytest.raises(ConfigValidationError):
            TopicConfig(topic="   ")

    def test_negative_slide_size_raises(self) -> None:
        with pytest.raises(ConfigValidationError, match="양수"):
            TopicConfig(topic="테스트", slide_width=-1)

    def test_output_dir_string_coercion(self) -> None:
        cfg = TopicConfig(topic="테스트", output_dir="./my_output")  # type: ignore[arg-type]
        assert isinstance(cfg.output_dir, Path)
        assert str(cfg.output_dir) == "my_output"

    def test_from_toml(self, sample_toml: Path) -> None:
        cfg = TopicConfig.from_toml(sample_toml)
        assert cfg.topic == "AI 트렌드 2025-2026"
        assert cfg.subtitle == "에이전틱 AI 시대"
        assert cfg.theme == "dark"
        assert len(cfg.sections) == 2
        assert cfg.sections[0].title == "개요"
        assert cfg.sections[1].slide_type == "timeline"

    def test_from_toml_file_not_found(self) -> None:
        with pytest.raises(ConfigFileNotFoundError, match="찾을 수 없습니다"):
            TopicConfig.from_toml(Path("/nonexistent/topic.toml"))

    def test_with_sections(self) -> None:
        sections = [
            SectionConfig(title="섹션 1"),
            SectionConfig(title="섹션 2", slide_type="timeline"),
        ]
        cfg = TopicConfig(topic="테스트", sections=sections)
        assert len(cfg.sections) == 2


class TestSectionConfig:
    def test_defaults(self) -> None:
        s = SectionConfig(title="개요")
        assert s.slide_type == "auto"
        assert s.conversion_strategy == "auto"
        assert s.content == ""

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ConfigValidationError, match="섹션 제목"):
            SectionConfig(title="")

    def test_invalid_strategy_raises(self) -> None:
        with pytest.raises(ConfigValidationError, match="허용 값"):
            SectionConfig(title="테스트", conversion_strategy="invalid")

    def test_valid_strategies(self) -> None:
        for strategy in ("auto", "pandoc", "custom"):
            s = SectionConfig(title="테스트", conversion_strategy=strategy)
            assert s.conversion_strategy == strategy


class TestSlideHint:
    def test_create(self) -> None:
        hint = SlideHint(section_index=0, slide_type="timeline")
        assert hint.section_index == 0
        assert hint.slide_type == "timeline"
        assert hint.conversion_strategy == "auto"
        assert hint.extra == {}
