"""template renderer 단위 테스트."""

from __future__ import annotations

import pytest

from ppt_maker.config import SectionConfig, TopicConfig
from ppt_maker.errors import TemplateError
from ppt_maker.template.filters import md_bullet, md_table, slide_hint
from ppt_maker.template.renderer import RenderedReport, TemplateRenderer, _parse_hints


class TestFilters:
    def test_md_table(self) -> None:
        data = [
            {"이름": "GPT-4", "회사": "OpenAI"},
            {"이름": "Claude", "회사": "Anthropic"},
        ]
        result = md_table(data)
        assert "| 이름" in result
        assert "| GPT-4" in result
        assert "---" in result

    def test_md_table_empty(self) -> None:
        assert md_table([]) == ""

    def test_md_bullet(self) -> None:
        result = md_bullet(["항목 1", "항목 2", "항목 3"])
        assert result == "- 항목 1\n- 항목 2\n- 항목 3"

    def test_md_bullet_indent(self) -> None:
        result = md_bullet(["하위 항목"], indent=1)
        assert result == "  - 하위 항목"

    def test_slide_hint(self) -> None:
        assert slide_hint("timeline") == "<!-- slide: type=timeline -->"

    def test_slide_hint_with_kwargs(self) -> None:
        result = slide_hint("table", strategy="custom")
        assert "type=table" in result
        assert "strategy=custom" in result


class TestParseHints:
    def test_basic_hint(self) -> None:
        md = "## 섹션 1\n<!-- slide: type=timeline -->\n내용"
        hints = _parse_hints(md)
        assert len(hints) == 1
        assert hints[0].slide_type == "timeline"
        assert hints[0].section_index == 1

    def test_multiple_hints(self) -> None:
        md = "## 섹션 1\n<!-- slide: type=timeline -->\n## 섹션 2\n<!-- slide: type=comparison -->"
        hints = _parse_hints(md)
        assert len(hints) == 2
        assert hints[0].slide_type == "timeline"
        assert hints[1].slide_type == "comparison"

    def test_hint_with_strategy(self) -> None:
        md = "<!-- slide: type=table, strategy=custom -->"
        hints = _parse_hints(md)
        assert len(hints) == 1
        assert hints[0].conversion_strategy == "custom"

    def test_no_hints(self) -> None:
        md = "# 제목\n그냥 텍스트"
        assert _parse_hints(md) == []


class TestTemplateRenderer:
    def test_render_base_template(self) -> None:
        renderer = TemplateRenderer()
        config = TopicConfig(
            topic="AI 트렌드",
            subtitle="2025-2026",
            sections=[
                SectionConfig(title="개요", content="AI 기술 발전 현황"),
                SectionConfig(title="LLM 경쟁", slide_type="timeline"),
            ],
        )
        result = renderer.render("base.md.j2", config)
        assert isinstance(result, RenderedReport)
        assert "AI 트렌드" in result.markdown
        assert "개요" in result.markdown
        assert "AI 기술 발전 현황" in result.markdown
        assert result.metadata["section_count"] == 2

    def test_render_string(self) -> None:
        renderer = TemplateRenderer()
        config = TopicConfig(topic="테스트 주제")
        result = renderer.render_string("# {{ topic }}", config)
        assert result.markdown == "# 테스트 주제"

    def test_missing_template_raises(self) -> None:
        renderer = TemplateRenderer()
        config = TopicConfig(topic="테스트")
        with pytest.raises(TemplateError, match="찾을 수 없습니다"):
            renderer.render("nonexistent.md.j2", config)

    def test_undefined_variable_raises(self) -> None:
        renderer = TemplateRenderer()
        config = TopicConfig(topic="테스트")
        with pytest.raises(TemplateError, match="렌더링 실패"):
            renderer.render_string("{{ undefined_var }}", config)

    def test_korean_content_renders(self) -> None:
        renderer = TemplateRenderer()
        config = TopicConfig(
            topic="수입차 브랜드 IT 전략",
            sections=[SectionConfig(title="메르세데스-벤츠 디지털 전환", content="DMS/CRM 통합")],
        )
        result = renderer.render("base.md.j2", config)
        assert "수입차 브랜드" in result.markdown
        assert "메르세데스-벤츠" in result.markdown

    def test_slide_hints_in_rendered_output(self) -> None:
        renderer = TemplateRenderer()
        config = TopicConfig(
            topic="테스트",
            sections=[
                SectionConfig(title="섹션 1", slide_type="timeline"),
            ],
        )
        result = renderer.render("base.md.j2", config)
        assert len(result.slide_hints) >= 1
        type_hint_found = any(h.slide_type == "timeline" for h in result.slide_hints)
        assert type_hint_found
