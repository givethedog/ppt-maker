"""초안 생성 — 수집 정보 기반 마크다운 골격."""
from __future__ import annotations

import logging
from pathlib import Path

from ppt_maker.wizard.session import WizardSession

logger = logging.getLogger(__name__)

# 대상별 섹션 구성 프리셋
AUDIENCE_PRESETS: dict[str, list[dict]] = {
    "executive": [
        {"title": "Executive Summary", "slide_type": "title"},
        {"title": "현황 요약", "slide_type": "content"},
        {"title": "핵심 성과", "slide_type": "content"},
        {"title": "주요 이슈", "slide_type": "content"},
        {"title": "재무 영향", "slide_type": "comparison"},
        {"title": "액션 아이템", "slide_type": "content"},
        {"title": "타임라인", "slide_type": "timeline"},
        {"title": "Q&A", "slide_type": "keynote"},
    ],
    "team": [
        {"title": "개요", "slide_type": "title"},
        {"title": "배경 및 목적", "slide_type": "section"},
        {"title": "현황 분석", "slide_type": "content"},
        {"title": "기술 상세", "slide_type": "content"},
        {"title": "구현 방안", "slide_type": "content"},
        {"title": "비교 분석", "slide_type": "comparison"},
        {"title": "일정 계획", "slide_type": "timeline"},
        {"title": "다음 단계", "slide_type": "keynote"},
    ],
    "general": [
        {"title": "소개", "slide_type": "title"},
        {"title": "왜 중요한가?", "slide_type": "section"},
        {"title": "핵심 내용", "slide_type": "content"},
        {"title": "사례", "slide_type": "content"},
        {"title": "비교", "slide_type": "comparison"},
        {"title": "요약", "slide_type": "keynote"},
    ],
}


def run_draft(session: WizardSession) -> Path:
    """초안 마크다운 생성.

    Returns:
        생성된 draft.md 경로.
    """
    out_dir = session.get_output_path()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 프리셋 선택 + 슬라이드 수 조정
    preset = AUDIENCE_PRESETS.get(session.audience, AUDIENCE_PRESETS["team"])
    sections = _adjust_slide_count(preset, session.slide_count)

    # 마크다운 생성
    lines = [
        f"# {session.topic}",
        "",
    ]
    if session.subtitle:
        lines.append(f"*{session.subtitle}*")
        lines.append("")

    meta = f"**대상:** {session.audience} | **목적:** {session.purpose} | **톤:** {session.tone}"
    lines.append(meta)
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, sec in enumerate(sections, 1):
        lines.append(f"## {i}. {sec['title']}")
        lines.append("")
        lines.append(f"<!-- slide_type: {sec['slide_type']} -->")
        lines.append("")
        lines.append(f"*{session.topic}에 대한 {sec['title']} 내용이 여기에 채워집니다.*")
        lines.append("")

    md_content = "\n".join(lines)
    draft_path = out_dir / "draft.md"
    draft_path.write_text(md_content, encoding="utf-8")

    # 세션에 초안 섹션 저장
    session.sections = sections
    session.draft_md = "draft.md"

    logger.info("초안 생성 완료: %d개 섹션 → %s", len(sections), draft_path)
    return draft_path


def _adjust_slide_count(preset: list[dict], target: int) -> list[dict]:
    """프리셋을 목표 슬라이드 수에 맞게 조정."""
    if target >= len(preset):
        # 부족하면 content 슬라이드 추가
        result = list(preset)
        while len(result) < target:
            idx = len(result) - 1  # 마지막(keynote) 앞에 삽입
            result.insert(idx, {
                "title": f"추가 내용 {len(result) - len(preset) + 1}",
                "slide_type": "content",
            })
        return result
    else:
        # 초과하면 중간 content 슬라이드 축소 (첫/끝 유지)
        if target < 3:
            return preset[:target]
        result = [preset[0]]  # 첫 슬라이드 유지
        middle = preset[1:-1]
        keep = target - 2
        step = max(1, len(middle) // keep) if keep > 0 else 1
        result.extend(middle[::step][:keep])
        result.append(preset[-1])  # 마지막 슬라이드 유지
        return result[:target]
