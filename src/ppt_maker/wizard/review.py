"""인터랙티브 리뷰 — 섹션별 검토 및 LLM 재생성."""
from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ppt_maker.config import SectionConfig
from ppt_maker.research.generator import ContentGenerator
from ppt_maker.research.llm import LLMConfig
from ppt_maker.wizard.session import WizardSession

logger = logging.getLogger(__name__)
console = Console()


def run_review(session: WizardSession) -> Path:
    """인터랙티브 리뷰 루프.

    사용자가 섹션을 검토하고 수정 요청 → LLM 재생성 → 반복.
    'a'로 전체 승인, 'q'로 저장 후 종료.

    Returns:
        최종 review.md 경로.
    """
    sections = session.get_sections()
    if not sections:
        console.print("[red]리뷰할 섹션이 없습니다.[/]")
        return Path(session.output_dir) / "review.md"

    # LLM 클라이언트 (재생성용)
    llm_config = LLMConfig(
        api_base=session.llm_api_base,
        model=session.llm_model,
        api_key_env=session.llm_api_key_env,
    )
    generator = ContentGenerator(llm_config)

    # 이전 버전 기록 (undo용)
    history: list[list[SectionConfig]] = [list(sections)]

    while True:
        # 섹션 목록 표시
        _display_sections(sections)

        console.print(
            "\n[dim]번호: 섹션 수정 | v번호: 내용 보기 | "
            "a: 전체 승인 | u: 되돌리기 | q: 저장 후 종료[/]"
        )
        choice = Prompt.ask("선택", default="a")

        if choice.lower() == "a":
            # 전체 승인
            break

        elif choice.lower() == "q":
            # 저장 후 종료 (resume 가능)
            console.print("[yellow]리뷰를 저장합니다. 나중에 재개할 수 있습니다.[/]")
            break

        elif choice.lower() == "u":
            # undo
            if len(history) > 1:
                history.pop()
                sections = list(history[-1])
                console.print("[green]이전 버전으로 되돌렸습니다.[/]")
            else:
                console.print("[yellow]더 이상 되돌릴 수 없습니다.[/]")

        elif choice.lower().startswith("v"):
            # 내용 보기
            try:
                idx = int(choice[1:]) - 1
                if 0 <= idx < len(sections):
                    _display_section_detail(sections[idx], idx)
                else:
                    console.print("[red]잘못된 번호입니다.[/]")
            except ValueError:
                console.print("[red]잘못된 입력입니다.[/]")

        else:
            # 섹션 수정
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(sections):
                    sections = _edit_section(
                        generator,
                        session.topic,
                        sections,
                        idx,
                        history,
                    )
                else:
                    console.print("[red]잘못된 번호입니다.[/]")
            except ValueError:
                console.print("[red]숫자, a, u, q 중 하나를 입력하세요.[/]")

    # 결과 저장
    session.set_sections(sections)
    review_path = _save_review_md(session, sections)
    session.review_md = "review.md"

    return review_path


def _display_sections(sections: list[SectionConfig]) -> None:
    """섹션 목록 테이블 표시."""
    table = Table(title="섹션 목록", show_lines=False)
    table.add_column("#", style="cyan", width=4)
    table.add_column("제목", style="bold")
    table.add_column("타입", style="dim")
    table.add_column("길이", style="dim", justify="right")

    for i, sec in enumerate(sections, 1):
        content_len = len(sec.content) if sec.content else 0
        status = "✓" if content_len > 20 else "…"
        table.add_row(
            str(i), f"{status} {sec.title}", sec.slide_type, f"{content_len}자",
        )

    console.print(table)


def _display_section_detail(section: SectionConfig, idx: int) -> None:
    """섹션 상세 내용 표시."""
    content = section.content or "(내용 없음)"
    panel = Panel(
        content,
        title=f"[{idx + 1}] {section.title} ({section.slide_type})",
        border_style="blue",
    )
    console.print(panel)


def _edit_section(
    generator: ContentGenerator,
    topic: str,
    sections: list[SectionConfig],
    idx: int,
    history: list[list[SectionConfig]],
) -> list[SectionConfig]:
    """LLM으로 섹션 재생성."""
    section = sections[idx]
    console.print(f"\n[bold]수정 대상:[/] [{idx + 1}] {section.title}")

    # 현재 내용 미리보기 (짧게)
    preview = (section.content or "")[:200]
    if preview:
        console.print(f"[dim]현재: {preview}...[/]")

    instruction = Prompt.ask("수정 지시")
    if not instruction.strip():
        console.print("[yellow]수정을 건너뜁니다.[/]")
        return sections

    console.print("[bold blue]재생성 중...[/]")

    try:
        new_content = generator.regenerate_section(
            all_sections=sections,
            section_index=idx,
            instruction=instruction,
            topic=topic,
        )

        # 변경 전/후 비교
        console.print("\n[green]재생성 완료:[/]")
        panel = Panel(
            new_content,
            title=f"[{idx + 1}] {section.title} (수정됨)",
            border_style="green",
        )
        console.print(panel)

        if Confirm.ask("이 수정을 적용하시겠습니까?", default=True):
            new_sections = list(sections)
            new_sections[idx] = SectionConfig(
                title=section.title,
                content=new_content,
                slide_type=section.slide_type,
            )
            history.append(new_sections)
            console.print("[green]적용됨![/]")
            return new_sections
        else:
            console.print("[yellow]수정을 취소했습니다.[/]")
            return sections

    except Exception as e:
        console.print(f"[red]재생성 실패: {e}[/]")
        return sections


def _save_review_md(session: WizardSession, sections: list[SectionConfig]) -> Path:
    """리뷰 완료된 마크다운 저장."""
    out_dir = session.get_output_path()
    lines = [f"# {session.topic}", ""]
    if session.subtitle:
        lines.extend([f"*{session.subtitle}*", ""])

    for i, sec in enumerate(sections, 1):
        lines.append(f"## {i}. {sec.title}")
        lines.append("")
        lines.append(f"<!-- slide_type: {sec.slide_type} -->")
        lines.append("")
        lines.append(sec.content or "")
        lines.append("")

    review_path = out_dir / "review.md"
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return review_path
