"""위저드 리뷰 단계 테스트."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ppt_maker.config import SectionConfig
from ppt_maker.wizard.review import (
    _display_section_detail,  # noqa: F401
    _display_sections,
    _edit_section,
    _save_review_md,
    run_review,
)
from ppt_maker.wizard.session import WizardSession

# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_sections() -> list[SectionConfig]:
    """테스트용 섹션 목록."""
    return [
        SectionConfig(
            title="서론", content="이것은 서론 내용입니다. 충분히 긴 내용.", slide_type="title"
        ),
        SectionConfig(
            title="본론", content="본론의 상세 내용이 여기 있습니다.", slide_type="content"
        ),
        SectionConfig(title="결론", content="결론 요약입니다.", slide_type="keynote"),
    ]


@pytest.fixture
def session_with_sections(tmp_path: Path, sample_sections: list[SectionConfig]) -> WizardSession:
    """섹션이 있는 세션 픽스처."""
    session = WizardSession(output_dir=str(tmp_path), topic="테스트 주제", subtitle="부제목")
    session.set_sections(sample_sections)
    return session


@pytest.fixture
def empty_session(tmp_path: Path) -> WizardSession:
    """섹션이 없는 빈 세션 픽스처."""
    return WizardSession(output_dir=str(tmp_path), topic="빈 주제")


# ---------------------------------------------------------------------------
# _display_sections 테스트
# ---------------------------------------------------------------------------

def test_display_sections_empty_list() -> None:
    """빈 섹션 목록으로 _display_sections 호출 시 오류 없이 실행."""
    # 오류 없이 실행되어야 함
    _display_sections([])


def test_display_sections_with_valid_sections(sample_sections: list[SectionConfig]) -> None:
    """유효한 섹션 목록으로 _display_sections 호출 시 오류 없이 실행."""
    _display_sections(sample_sections)


def test_display_sections_with_short_content() -> None:
    """내용이 짧은 섹션 (20자 이하) 처리."""
    sections = [SectionConfig(title="짧은 섹션", content="짧음", slide_type="content")]
    _display_sections(sections)


def test_display_sections_with_no_content() -> None:
    """내용이 없는 섹션 처리."""
    sections = [SectionConfig(title="빈 섹션", content="", slide_type="content")]
    _display_sections(sections)


# ---------------------------------------------------------------------------
# _save_review_md 테스트
# ---------------------------------------------------------------------------

def test_save_review_md_creates_file(
    session_with_sections: WizardSession,
    sample_sections: list[SectionConfig],
) -> None:
    """리뷰 마크다운 파일이 올바르게 생성되어야 함."""
    review_path = _save_review_md(session_with_sections, sample_sections)

    assert review_path.exists()
    assert review_path.name == "review.md"


def test_save_review_md_contains_topic(
    session_with_sections: WizardSession,
    sample_sections: list[SectionConfig],
) -> None:
    """리뷰 마크다운에 주제가 포함되어야 함."""
    review_path = _save_review_md(session_with_sections, sample_sections)
    content = review_path.read_text(encoding="utf-8")

    assert "테스트 주제" in content


def test_save_review_md_contains_subtitle(
    session_with_sections: WizardSession,
    sample_sections: list[SectionConfig],
) -> None:
    """리뷰 마크다운에 부제목이 포함되어야 함."""
    review_path = _save_review_md(session_with_sections, sample_sections)
    content = review_path.read_text(encoding="utf-8")

    assert "부제목" in content


def test_save_review_md_contains_sections(
    session_with_sections: WizardSession,
    sample_sections: list[SectionConfig],
) -> None:
    """리뷰 마크다운에 모든 섹션 제목이 포함되어야 함."""
    review_path = _save_review_md(session_with_sections, sample_sections)
    content = review_path.read_text(encoding="utf-8")

    for sec in sample_sections:
        assert sec.title in content


def test_save_review_md_contains_slide_type_comments(
    session_with_sections: WizardSession,
    sample_sections: list[SectionConfig],
) -> None:
    """리뷰 마크다운에 slide_type 주석이 포함되어야 함."""
    review_path = _save_review_md(session_with_sections, sample_sections)
    content = review_path.read_text(encoding="utf-8")

    assert "<!-- slide_type: title -->" in content
    assert "<!-- slide_type: content -->" in content
    assert "<!-- slide_type: keynote -->" in content


def test_save_review_md_no_subtitle(tmp_path: Path, sample_sections: list[SectionConfig]) -> None:
    """부제목 없는 세션에서도 정상 동작."""
    session = WizardSession(output_dir=str(tmp_path), topic="주제만")
    session.set_sections(sample_sections)
    review_path = _save_review_md(session, sample_sections)

    content = review_path.read_text(encoding="utf-8")
    assert "주제만" in content


# ---------------------------------------------------------------------------
# run_review 테스트
# ---------------------------------------------------------------------------

def test_run_review_returns_path_on_approve(
    session_with_sections: WizardSession,
) -> None:
    """'a' 입력으로 전체 승인 시 review.md 경로 반환."""
    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.return_value = "a"
        result = run_review(session_with_sections)

    assert isinstance(result, Path)
    assert result.name == "review.md"


def test_run_review_creates_file_on_approve(
    session_with_sections: WizardSession,
) -> None:
    """'a' 입력으로 전체 승인 시 review.md 파일이 실제로 생성됨."""
    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.return_value = "a"
        result = run_review(session_with_sections)

    assert result.exists()


def test_run_review_sets_review_md_on_session(
    session_with_sections: WizardSession,
) -> None:
    """run_review 후 session.review_md 가 설정되어야 함."""
    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.return_value = "a"
        run_review(session_with_sections)

    assert session_with_sections.review_md == "review.md"


def test_run_review_empty_sections_returns_path(empty_session: WizardSession) -> None:
    """섹션이 없는 경우 review.md 경로를 반환하고 오류 없이 종료."""
    result = run_review(empty_session)

    assert isinstance(result, Path)
    assert result.name == "review.md"


def test_run_review_quit_with_q(session_with_sections: WizardSession) -> None:
    """'q' 입력으로 저장 후 종료."""
    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.return_value = "q"
        result = run_review(session_with_sections)

    assert isinstance(result, Path)
    assert result.exists()


def test_run_review_undo_then_approve(session_with_sections: WizardSession) -> None:
    """'u' 입력 후 'a' 입력으로 정상 완료."""
    responses = ["u", "a"]
    response_iter = iter(responses)

    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.side_effect = lambda *args, **kwargs: next(response_iter)
        result = run_review(session_with_sections)

    assert result.exists()


def test_run_review_view_section_then_approve(session_with_sections: WizardSession) -> None:
    """'v1' 입력으로 섹션 내용 보기 후 'a' 입력으로 완료."""
    responses = ["v1", "a"]
    response_iter = iter(responses)

    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.side_effect = lambda *args, **kwargs: next(response_iter)
        result = run_review(session_with_sections)

    assert result.exists()


def test_run_review_invalid_input_then_approve(session_with_sections: WizardSession) -> None:
    """잘못된 입력 후 'a' 입력으로 정상 완료."""
    responses = ["xyz", "a"]
    response_iter = iter(responses)

    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.side_effect = lambda *args, **kwargs: next(response_iter)
        result = run_review(session_with_sections)

    assert result.exists()


# ---------------------------------------------------------------------------
# _edit_section 테스트
# ---------------------------------------------------------------------------

def test_edit_section_applies_changes(
    sample_sections: list[SectionConfig],
) -> None:
    """LLM 재생성 후 확인 시 섹션 내용이 업데이트되어야 함."""
    mock_generator = MagicMock()
    mock_generator.regenerate_section.return_value = "새로운 내용입니다."
    history: list[list[SectionConfig]] = [list(sample_sections)]

    with (
        patch("ppt_maker.wizard.review.Prompt") as mock_prompt,
        patch("ppt_maker.wizard.review.Confirm") as mock_confirm,
    ):
        mock_prompt.ask.return_value = "더 자세하게 설명해주세요"
        mock_confirm.ask.return_value = True

        result = _edit_section(mock_generator, "테스트 주제", sample_sections, 0, history)

    assert result[0].content == "새로운 내용입니다."
    assert len(history) == 2  # 원본 + 수정 후


def test_edit_section_rejects_changes(
    sample_sections: list[SectionConfig],
) -> None:
    """LLM 재생성 후 거절 시 원본 섹션 반환."""
    original_content = sample_sections[0].content
    mock_generator = MagicMock()
    mock_generator.regenerate_section.return_value = "새로운 내용입니다."
    history: list[list[SectionConfig]] = [list(sample_sections)]

    with (
        patch("ppt_maker.wizard.review.Prompt") as mock_prompt,
        patch("ppt_maker.wizard.review.Confirm") as mock_confirm,
    ):
        mock_prompt.ask.return_value = "수정 지시"
        mock_confirm.ask.return_value = False

        result = _edit_section(mock_generator, "테스트 주제", sample_sections, 0, history)

    assert result[0].content == original_content
    assert len(history) == 1  # 변경 없음


def test_edit_section_empty_instruction_skips(
    sample_sections: list[SectionConfig],
) -> None:
    """빈 수정 지시 입력 시 변경 없이 원본 반환."""
    mock_generator = MagicMock()
    history: list[list[SectionConfig]] = [list(sample_sections)]

    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.return_value = "   "  # 공백만 입력

        result = _edit_section(mock_generator, "테스트 주제", sample_sections, 0, history)

    mock_generator.regenerate_section.assert_not_called()
    assert result is sample_sections


def test_edit_section_generator_exception(
    sample_sections: list[SectionConfig],
) -> None:
    """LLM 재생성 실패 시 원본 섹션 반환."""
    mock_generator = MagicMock()
    mock_generator.regenerate_section.side_effect = RuntimeError("API 오류")
    history: list[list[SectionConfig]] = [list(sample_sections)]

    with patch("ppt_maker.wizard.review.Prompt") as mock_prompt:
        mock_prompt.ask.return_value = "수정 지시"

        result = _edit_section(mock_generator, "테스트 주제", sample_sections, 0, history)

    assert result is sample_sections


# ---------------------------------------------------------------------------
# wizard CLI 명령 등록 확인
# ---------------------------------------------------------------------------

def test_wizard_command_registered() -> None:
    """wizard 명령이 CLI 앱에 등록되어 있어야 함."""
    from typer.testing import CliRunner

    from ppt_maker.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["wizard", "--help"])

    assert result.exit_code == 0
    assert "위저드" in result.output or "wizard" in result.output.lower()


def test_wizard_command_help_contains_output_option() -> None:
    """wizard --help 출력에 --output 옵션이 있어야 함."""
    from typer.testing import CliRunner

    from ppt_maker.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["wizard", "--help"])

    assert "--output" in result.output or "-o" in result.output


def test_wizard_command_help_contains_resume_option() -> None:
    """wizard --help 출력에 --resume 옵션이 있어야 함."""
    from typer.testing import CliRunner

    from ppt_maker.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["wizard", "--help"])

    assert "--resume" in result.output or "-r" in result.output
