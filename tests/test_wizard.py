"""위저드 핵심 모듈 테스트."""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from ppt_maker.config import SectionConfig
from ppt_maker.research.generator import (
    REGENERATE_SYSTEM_PROMPT,
    ContentGenerator,
    GeneratedContent,
)
from ppt_maker.research.llm import LLMConfig
from ppt_maker.wizard.draft import AUDIENCE_PRESETS, _adjust_slide_count, run_draft
from ppt_maker.wizard.research import run_research
from ppt_maker.wizard.session import (
    STAGE_ORDER,
    WizardSession,
    load_session,
    save_session,
)

# ---------------------------------------------------------------------------
# WizardSession 기본값 및 __post_init__
# ---------------------------------------------------------------------------


class TestWizardSessionDefaults:
    """WizardSession 기본값 및 초기화 검증."""

    def test_session_id_auto_generated(self) -> None:
        session = WizardSession()
        assert len(session.session_id) == 8

    def test_session_id_preserved_when_given(self) -> None:
        session = WizardSession(session_id="abc12345")
        assert session.session_id == "abc12345"

    def test_created_at_auto_set(self) -> None:
        session = WizardSession()
        assert session.created_at != ""

    def test_updated_at_auto_set(self) -> None:
        session = WizardSession()
        assert session.updated_at != ""

    def test_default_stage_is_collect(self) -> None:
        session = WizardSession()
        assert session.current_stage == "collect"

    def test_default_values(self) -> None:
        session = WizardSession()
        assert session.output_dir == "./output"
        assert session.audience == "team"
        assert session.purpose == "report"
        assert session.slide_count == 8
        assert session.tone == "professional"
        assert session.llm_model == "gpt-4o-mini"
        assert session.sections == []

    def test_stage_order(self) -> None:
        assert STAGE_ORDER == ["collect", "draft", "research", "review", "generate", "done"]


# ---------------------------------------------------------------------------
# save_session / load_session 왕복 테스트
# ---------------------------------------------------------------------------


class TestSaveLoadSession:
    """세션 저장 및 로드 왕복 검증."""

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="테스트 주제",
            subtitle="부제",
            output_dir=str(tmp_path),
        )
        path = save_session(session)
        assert path.exists()

        loaded = load_session(path)
        assert loaded.session_id == session.session_id
        assert loaded.topic == session.topic
        assert loaded.subtitle == session.subtitle
        assert loaded.current_stage == session.current_stage

    def test_saved_filename_is_session_json(self, tmp_path: Path) -> None:
        session = WizardSession(output_dir=str(tmp_path))
        path = save_session(session)
        assert path.name == "session.json"

    def test_saved_content_is_valid_json(self, tmp_path: Path) -> None:
        session = WizardSession(topic="주제", output_dir=str(tmp_path))
        path = save_session(session)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "session_id" in data
        assert "topic" in data

    def test_output_dir_created_if_missing(self, tmp_path: Path) -> None:
        new_dir = tmp_path / "new_subdir"
        session = WizardSession(output_dir=str(new_dir))
        save_session(session)
        assert new_dir.exists()


# ---------------------------------------------------------------------------
# get_sections / set_sections
# ---------------------------------------------------------------------------


class TestSectionConversion:
    """SectionConfig 변환 메서드 검증."""

    def test_set_sections_stores_dicts(self) -> None:
        session = WizardSession()
        configs = [
            SectionConfig(title="소개", content="내용", slide_type="content"),
            SectionConfig(title="결론", content="정리", slide_type="keynote"),
        ]
        session.set_sections(configs)
        assert len(session.sections) == 2
        assert session.sections[0]["title"] == "소개"
        assert session.sections[1]["slide_type"] == "keynote"

    def test_get_sections_returns_section_configs(self) -> None:
        session = WizardSession()
        session.sections = [
            {"title": "섹션1", "content": "내용1", "slide_type": "content"},
        ]
        result = session.get_sections()
        assert len(result) == 1
        assert isinstance(result[0], SectionConfig)
        assert result[0].title == "섹션1"

    def test_set_then_get_roundtrip(self) -> None:
        session = WizardSession()
        original = [
            SectionConfig(title="A", content="내용A", slide_type="title"),
            SectionConfig(title="B", content="내용B", slide_type="content"),
        ]
        session.set_sections(original)
        recovered = session.get_sections()
        assert len(recovered) == 2
        assert recovered[0].title == "A"
        assert recovered[1].content == "내용B"

    def test_empty_sections_returns_empty_list(self) -> None:
        session = WizardSession()
        assert session.get_sections() == []


# ---------------------------------------------------------------------------
# advance_stage
# ---------------------------------------------------------------------------


class TestAdvanceStage:
    """스테이지 전환 검증."""

    def test_stage_transitions(self) -> None:
        session = WizardSession()
        session.advance_stage("draft")
        assert session.current_stage == "draft"

    def test_updated_at_refreshed_on_advance(self) -> None:
        session = WizardSession()
        old_updated = session.updated_at
        time.sleep(0.01)
        session.advance_stage("research")
        assert session.updated_at >= old_updated

    def test_advance_through_all_stages(self) -> None:
        session = WizardSession()
        for stage in STAGE_ORDER[1:]:
            session.advance_stage(stage)
        assert session.current_stage == "done"


# ---------------------------------------------------------------------------
# run_draft — 다양한 audience 테스트
# ---------------------------------------------------------------------------


class TestRunDraft:
    """run_draft 함수 검증."""

    def test_team_audience_default(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="클라우드 전환",
            audience="team",
            slide_count=8,
            output_dir=str(tmp_path),
        )
        path = run_draft(session)
        assert path.exists()
        assert path.name == "draft.md"
        content = path.read_text(encoding="utf-8")
        assert "클라우드 전환" in content

    def test_executive_audience(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="연간 보고",
            audience="executive",
            slide_count=8,
            output_dir=str(tmp_path),
        )
        run_draft(session)
        assert len(session.sections) == 8
        assert session.draft_md == "draft.md"

    def test_general_audience(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="신기술 소개",
            audience="general",
            slide_count=6,
            output_dir=str(tmp_path),
        )
        run_draft(session)
        assert len(session.sections) == 6

    def test_subtitle_included_in_output(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="주제",
            subtitle="부제목",
            output_dir=str(tmp_path),
        )
        path = run_draft(session)
        content = path.read_text(encoding="utf-8")
        assert "부제목" in content

    def test_unknown_audience_falls_back_to_team(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="테스트",
            audience="unknown_type",
            slide_count=8,
            output_dir=str(tmp_path),
        )
        run_draft(session)
        assert len(session.sections) == 8


# ---------------------------------------------------------------------------
# _adjust_slide_count 확장 및 축소
# ---------------------------------------------------------------------------


class TestAdjustSlideCount:
    """_adjust_slide_count 함수 검증."""

    def setup_method(self) -> None:
        self.preset = AUDIENCE_PRESETS["team"]  # 8개 슬라이드

    def test_same_count_no_change(self) -> None:
        result = _adjust_slide_count(self.preset, 8)
        assert len(result) == 8

    def test_expand_to_10(self) -> None:
        result = _adjust_slide_count(self.preset, 10)
        assert len(result) == 10

    def test_expand_preserves_first_and_last(self) -> None:
        result = _adjust_slide_count(self.preset, 10)
        assert result[0]["title"] == self.preset[0]["title"]
        assert result[-1]["title"] == self.preset[-1]["title"]

    def test_contract_to_5(self) -> None:
        result = _adjust_slide_count(self.preset, 5)
        assert len(result) == 5

    def test_contract_preserves_first_and_last(self) -> None:
        result = _adjust_slide_count(self.preset, 5)
        assert result[0]["title"] == self.preset[0]["title"]
        assert result[-1]["title"] == self.preset[-1]["title"]

    def test_target_2_or_less(self) -> None:
        result = _adjust_slide_count(self.preset, 2)
        assert len(result) == 2

    def test_target_1(self) -> None:
        result = _adjust_slide_count(self.preset, 1)
        assert len(result) == 1

    def test_expanded_slides_are_content_type(self) -> None:
        result = _adjust_slide_count(self.preset, 12)
        extra = [s for s in result if s not in self.preset]
        for s in extra:
            assert s["slide_type"] == "content"


# ---------------------------------------------------------------------------
# run_research — ContentGenerator 모킹
# ---------------------------------------------------------------------------


class TestRunResearch:
    """run_research 함수 검증 (LLM 모킹)."""

    def test_research_md_created(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="AI 트렌드",
            subtitle="2024년",
            audience="team",
            output_dir=str(tmp_path),
        )
        session.sections = [
            {"title": "개요", "content": "", "slide_type": "title"},
            {"title": "현황", "content": "", "slide_type": "content"},
        ]

        mock_generated = GeneratedContent(
            sections=[
                SectionConfig(title="개요", content="AI 개요 내용", slide_type="title"),
                SectionConfig(title="현황", content="AI 현황 내용", slide_type="content"),
            ]
        )

        with patch.object(ContentGenerator, "generate_with_outline", return_value=mock_generated):
            path = run_research(session)

        assert path.exists()
        assert path.name == "research.md"
        content = path.read_text(encoding="utf-8")
        assert "AI 트렌드" in content
        assert "AI 개요 내용" in content

    def test_session_sections_updated(self, tmp_path: Path) -> None:
        session = WizardSession(
            topic="주제",
            output_dir=str(tmp_path),
        )
        session.sections = [{"title": "섹션", "content": "", "slide_type": "content"}]

        mock_generated = GeneratedContent(
            sections=[SectionConfig(title="섹션", content="상세 내용", slide_type="content")]
        )

        with patch.object(ContentGenerator, "generate_with_outline", return_value=mock_generated):
            run_research(session)

        assert session.research_md == "research.md"
        assert session.sections[0]["content"] == "상세 내용"

    def test_works_without_subtitle(self, tmp_path: Path) -> None:
        session = WizardSession(topic="주제", output_dir=str(tmp_path))
        session.sections = [{"title": "개요", "content": "", "slide_type": "content"}]

        mock_generated = GeneratedContent(
            sections=[SectionConfig(title="개요", content="내용", slide_type="content")]
        )

        with patch.object(ContentGenerator, "generate_with_outline", return_value=mock_generated):
            path = run_research(session)

        assert path.exists()


# ---------------------------------------------------------------------------
# generate_with_outline — LLM 모킹
# ---------------------------------------------------------------------------


class TestGenerateWithOutline:
    """ContentGenerator.generate_with_outline 검증."""

    def _make_generator(self) -> ContentGenerator:
        return ContentGenerator(LLMConfig())

    def test_parses_valid_json(self) -> None:
        generator = self._make_generator()
        mock_response = json.dumps({
            "sections": [
                {"title": "소개", "content": "소개 내용", "slide_type": "title"},
                {"title": "본론", "content": "본론 내용", "slide_type": "content"},
            ]
        })

        mock_client = MagicMock()
        mock_client.chat.return_value = mock_response
        generator._client = mock_client

        result = generator.generate_with_outline(
            topic="테스트",
            outline=["소개", "본론"],
            audience="team",
        )

        assert len(result.sections) == 2
        assert result.sections[0].title == "소개"
        assert result.sections[1].content == "본론 내용"

    def test_works_without_outline(self) -> None:
        generator = self._make_generator()
        mock_response = json.dumps({
            "sections": [{"title": "개요", "content": "내용", "slide_type": "content"}]
        })

        mock_client = MagicMock()
        mock_client.chat.return_value = mock_response
        generator._client = mock_client

        result = generator.generate_with_outline(topic="주제")
        assert len(result.sections) == 1

    def test_fallback_single_section_on_parse_failure(self) -> None:
        generator = self._make_generator()
        mock_client = MagicMock()
        mock_client.chat.return_value = "파싱 불가 텍스트"
        generator._client = mock_client

        result = generator.generate_with_outline(topic="주제", outline=["섹션1"])
        assert len(result.sections) == 1
        assert result.sections[0].title == "주제"

    def test_raw_response_stored(self) -> None:
        generator = self._make_generator()
        raw = json.dumps({"sections": [{"title": "T", "content": "C", "slide_type": "content"}]})
        mock_client = MagicMock()
        mock_client.chat.return_value = raw
        generator._client = mock_client

        result = generator.generate_with_outline(topic="주제")
        assert result.raw_response == raw


# ---------------------------------------------------------------------------
# regenerate_section — LLM 모킹
# ---------------------------------------------------------------------------


class TestRegenerateSection:
    """ContentGenerator.regenerate_section 검증."""

    def _make_generator(self) -> ContentGenerator:
        return ContentGenerator(LLMConfig())

    def test_returns_modified_content(self) -> None:
        generator = self._make_generator()
        mock_client = MagicMock()
        mock_client.chat.return_value = "수정된 마크다운 내용"
        generator._client = mock_client

        sections = [
            SectionConfig(title="소개", content="원본 내용", slide_type="content"),
            SectionConfig(title="결론", content="결론 내용", slide_type="keynote"),
        ]

        result = generator.regenerate_section(
            all_sections=sections,
            section_index=0,
            instruction="더 상세하게 작성해주세요",
            topic="전체 주제",
        )

        assert result == "수정된 마크다운 내용"

    def test_uses_regenerate_system_prompt(self) -> None:
        generator = self._make_generator()
        mock_client = MagicMock()
        mock_client.chat.return_value = "결과"
        generator._client = mock_client

        sections = [SectionConfig(title="섹션", content="내용", slide_type="content")]
        generator.regenerate_section(
            all_sections=sections,
            section_index=0,
            instruction="수정 요청",
            topic="주제",
        )

        call_args = mock_client.chat.call_args
        assert call_args[0][0] == REGENERATE_SYSTEM_PROMPT

    def test_user_prompt_includes_full_outline(self) -> None:
        generator = self._make_generator()
        mock_client = MagicMock()
        mock_client.chat.return_value = "결과"
        generator._client = mock_client

        sections = [
            SectionConfig(title="섹션A", content="내용A", slide_type="content"),
            SectionConfig(title="섹션B", content="내용B", slide_type="keynote"),
        ]
        generator.regenerate_section(
            all_sections=sections,
            section_index=0,
            instruction="개선",
            topic="주제",
        )

        user_prompt = mock_client.chat.call_args[0][1]
        assert "섹션A" in user_prompt
        assert "섹션B" in user_prompt
        assert "개선" in user_prompt


# ---------------------------------------------------------------------------
# _parse_sections — 두 generate 메서드에서 공통 사용
# ---------------------------------------------------------------------------


class TestParseSections:
    """_parse_sections 메서드 검증."""

    def _make_generator(self) -> ContentGenerator:
        return ContentGenerator(LLMConfig())

    def test_parses_valid_json(self) -> None:
        generator = self._make_generator()
        raw = json.dumps({
            "sections": [
                {"title": "T1", "content": "C1", "slide_type": "content"},
                {"title": "T2", "content": "C2", "slide_type": "keynote"},
            ]
        })
        sections = generator._parse_sections(raw, "폴백주제")
        assert len(sections) == 2
        assert sections[0].title == "T1"
        assert sections[1].slide_type == "keynote"

    def test_strips_code_block_wrapper(self) -> None:
        generator = self._make_generator()
        inner = json.dumps({"sections": [{"title": "T", "content": "C", "slide_type": "content"}]})
        raw = f"```json\n{inner}\n```"
        sections = generator._parse_sections(raw, "폴백")
        assert len(sections) == 1
        assert sections[0].title == "T"

    def test_fallback_single_section_on_failure(self) -> None:
        generator = self._make_generator()
        sections = generator._parse_sections("not json at all", "폴백주제")
        assert len(sections) == 1
        assert sections[0].title == "폴백주제"
        assert sections[0].content == "not json at all"

    def test_generate_and_generate_with_outline_share_parsing(self) -> None:
        """두 메서드 모두 _parse_sections를 사용하는지 간접 검증."""
        generator = self._make_generator()
        raw = json.dumps({
            "sections": [{"title": "공통", "content": "내용", "slide_type": "content"}]
        })

        mock_client = MagicMock()
        mock_client.chat.return_value = raw
        generator._client = mock_client

        result1 = generator.generate(topic="주제")
        mock_client.chat.return_value = raw
        result2 = generator.generate_with_outline(topic="주제")

        assert result1.sections[0].title == result2.sections[0].title
