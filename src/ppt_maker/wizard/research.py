"""LLM 리서치 — 초안 섹션을 상세 콘텐츠로 보강."""
from __future__ import annotations

import logging
from pathlib import Path

from ppt_maker.research.generator import ContentGenerator
from ppt_maker.research.llm import LLMConfig
from ppt_maker.wizard.session import WizardSession

logger = logging.getLogger(__name__)


def run_research(session: WizardSession) -> Path:
    """LLM으로 초안 섹션을 상세 콘텐츠로 보강.

    Returns:
        생성된 research.md 경로.
    """
    llm_config = LLMConfig(
        api_base=session.llm_api_base,
        model=session.llm_model,
        api_key_env=session.llm_api_key_env,
    )
    generator = ContentGenerator(llm_config)

    # 초안 섹션 제목 리스트를 포함한 보강 요청
    section_titles = [s.get("title", "") for s in session.sections]

    generated = generator.generate_with_outline(
        topic=session.topic,
        subtitle=session.subtitle,
        outline=section_titles,
        audience=session.audience,
        purpose=session.purpose,
        tone=session.tone,
    )

    # 세션 업데이트
    session.set_sections(generated.sections)

    # 리서치 마크다운 저장
    out_dir = session.get_output_path()
    research_path = out_dir / "research.md"

    lines = [f"# {session.topic}", ""]
    if session.subtitle:
        lines.extend([f"*{session.subtitle}*", ""])
    lines.extend([
        f"**대상:** {session.audience} | **목적:** {session.purpose} | **톤:** {session.tone}",
        "", "---", "",
    ])

    for i, sec in enumerate(generated.sections, 1):
        lines.append(f"## {i}. {sec.title}")
        lines.append("")
        lines.append(f"<!-- slide_type: {sec.slide_type} -->")
        lines.append("")
        lines.append(sec.content)
        lines.append("")

    research_path.write_text("\n".join(lines), encoding="utf-8")
    session.research_md = "research.md"

    logger.info("리서치 완료: %d개 섹션 보강 → %s", len(generated.sections), research_path)
    return research_path
