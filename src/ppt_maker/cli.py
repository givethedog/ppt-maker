"""CLI 인터페이스 (Typer 기반)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from dotenv import load_dotenv
from rich.console import Console

from ppt_maker import __version__
from ppt_maker.errors import PptMakerError

if TYPE_CHECKING:
    from ppt_maker.wizard.session import WizardSession

load_dotenv()

app = typer.Typer(
    name="ppt-maker",
    help="주제 하나만 입력하면, 조사부터 보고서, 프레젠테이션까지 자동으로.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"ppt-maker {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="버전 정보 출력",
    ),
) -> None:
    """ppt-maker: 범용 보고서 + 프레젠테이션 자동 생성 파이프라인."""


@app.command()
def generate(  # noqa: B008
    topic: str = typer.Argument(..., help="생성할 주제 (예: 'AI 트렌드 2025-2026')"),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="TOML 설정 파일 경로",
    ),
    theme: str = typer.Option("default", "--theme", "-t", help="테마 이름"),
    output_dir: Path = typer.Option(
        Path("./output"), "--output", "-o", help="출력 디렉토리",
    ),
    no_research: bool = typer.Option(
        False, "--no-research", help="LLM 콘텐츠 생성을 건너뜁니다",
    ),
) -> None:
    """주제에 대한 보고서(.md)와 프레젠테이션(.pptx)을 생성합니다."""
    try:
        from ppt_maker.config import TopicConfig
        from ppt_maker.pipeline import run_pipeline

        if config:
            topic_config = TopicConfig.from_toml(config)
        else:
            topic_config = TopicConfig(topic=topic, theme=theme, output_dir=output_dir)

        if no_research:
            topic_config.use_research = False

        # 템플릿 등록 확인
        from ppt_maker.workspace import is_template_registered

        if not is_template_registered():
            console.print(
                "[bold yellow]⚠ 회사 템플릿이 등록되지 않았습니다.[/]\n"
                "  [dim]ppt-maker init --template <파일> 로 등록하면 회사 디자인이 적용됩니다.[/]\n"
            )

        console.print(f"\n[bold]ppt-maker[/] v{__version__}")
        console.print(f"[blue]주제:[/] {topic_config.topic}")
        console.print(f"[blue]테마:[/] {topic_config.theme}")
        console.print(f"[blue]출력:[/] {topic_config.output_dir}\n")

        result = run_pipeline(topic_config)

        console.print("\n[bold green]완료![/]")
        if result.markdown_path:
            console.print(f"  마크다운: {result.markdown_path}")
        if result.pptx_path:
            console.print(f"  PPTX:     {result.pptx_path} ({result.slide_count}장)")
        console.print(f"  소요시간: {result.elapsed_seconds:.1f}초")

    except PptMakerError as e:
        console.print(f"[bold red]오류:[/] {e}", err=True)
        if e.detail:
            console.print(f"[dim]{e.detail}[/]", err=True)
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[bold red]예상치 못한 오류:[/] {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def themes() -> None:
    """사용 가능한 테마 목록을 출력합니다."""
    from ppt_maker.theme.manager import ThemeManager

    tm = ThemeManager()
    theme_list = tm.list_themes()
    if not theme_list:
        console.print("[yellow]사용 가능한 테마가 없습니다.[/]")
        return

    console.print("[bold]사용 가능한 테마:[/]\n")
    for name in theme_list:
        theme = tm.load_theme(name)
        console.print(f"  [cyan]{name}[/] — {theme.description}")


@app.command()
def init(  # noqa: B008
    template: Path = typer.Option(
        ..., "--template", "-t", help="회사 템플릿 .pptx 파일 경로",
    ),
    name: str = typer.Option(
        "company", "--name", "-n", help="템플릿 이름 (기본: company)",
    ),
) -> None:
    """회사 템플릿을 등록합니다. 최초 1회 실행."""
    try:
        from ppt_maker.workspace import register_template

        console.print("\n[bold]ppt-maker[/] 템플릿 등록\n")
        console.print(f"  파일: {template}")
        console.print(f"  이름: {name}\n")

        template_dir = register_template(template, name)

        console.print("[bold green]템플릿 등록 완료![/]\n")
        console.print(f"  저장 위치: {template_dir}")

        # 분석 결과 요약 출력
        from ppt_maker.template.analyzer import load_manifest

        manifest_path = template_dir / "manifest.toml"
        if manifest_path.exists():
            manifest = load_manifest(manifest_path)
            w, h = manifest.slide_width, manifest.slide_height
            console.print(f"  슬라이드 크기: {w:.1f} x {h:.1f} inches")
            console.print(f"  레이아웃: {len(manifest.layouts)}개 감지")
            if manifest.layout_mapping:
                console.print("  자동 매핑:")
                for ppt_type, idx in sorted(manifest.layout_mapping.items()):
                    console.print(f"    {ppt_type} → [{idx}] {manifest.layouts[idx].name}")

    except PptMakerError as e:
        console.print(f"[bold red]오류:[/] {e}", err=True)
        if e.detail:
            console.print(f"[dim]{e.detail}[/]", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def check() -> None:
    """환경 의존성을 검증합니다 (pandoc, 폰트, 템플릿 등)."""
    console.print(f"[bold]ppt-maker[/] v{__version__} 환경 검증\n")

    # Python
    import sys

    console.print(f"  Python:  {sys.version.split()[0]} [green]OK[/]")

    # pandoc
    pandoc_path = shutil.which("pandoc")
    if pandoc_path:
        from ppt_maker.converter.pandoc import check_pandoc

        version = check_pandoc()
        console.print(f"  pandoc:  {version} [green]OK[/]")
    else:
        console.print("  pandoc:  [red]미설치[/] (brew install pandoc)")

    # 한글 폰트
    from ppt_maker.fonts.resolver import resolve_font

    font = resolve_font()
    status = "[green]OK[/]" if not font.is_fallback else "[yellow]폴백[/]"
    console.print(f"  한글폰트: {font.name} {status}")

    # 테마
    from ppt_maker.theme.manager import ThemeManager

    tm = ThemeManager()
    theme_count = len(tm.list_themes())
    console.print(f"  테마:    {theme_count}개 사용 가능 [green]OK[/]")

    # 템플릿 등록 상태
    from ppt_maker.workspace import get_registered_template, is_template_registered

    if is_template_registered():
        tpl_path = get_registered_template()
        console.print(f"  템플릿:  [green]등록됨[/] ({tpl_path})")
    else:
        console.print("  템플릿:  [yellow]미등록[/] (ppt-maker init --template <파일> 으로 등록)")


@app.command()
def wizard(
    output_dir: Path = typer.Option(
        Path("./output"), "--output", "-o", help="출력 디렉토리",
    ),
    resume: Path | None = typer.Option(
        None, "--resume", "-r", help="세션 파일에서 재개 (예: output/session.json)",
    ),
) -> None:
    """대화형 위저드 — 단계별로 프레젠테이션을 생성합니다."""
    try:
        from ppt_maker.wizard.session import (
            WizardSession,
            load_session,
            save_session,
        )

        # 세션 초기화 or 재개
        if resume and resume.exists():
            session = load_session(resume)
            console.print(f"\n[bold]세션 재개:[/] {session.session_id}")
            console.print(f"[dim]현재 단계: {session.current_stage}[/]\n")
        else:
            session = WizardSession(output_dir=str(output_dir))
            console.print("\n[bold]ppt-maker[/] 위저드\n")

        # Stage 1: Collect (if needed)
        if session.current_stage == "collect":
            _wizard_collect(session)
            session.advance_stage("draft")
            save_session(session)

        # Stage 2: Draft
        if session.current_stage == "draft":
            console.print("\n[bold blue]초안 생성 중...[/]")
            from ppt_maker.wizard.draft import run_draft
            draft_path = run_draft(session)
            console.print(f"[green]초안 저장:[/] {draft_path}")
            console.print("[dim]draft.md를 직접 편집할 수도 있습니다.[/]\n")
            session.advance_stage("research")
            save_session(session)

        # Stage 3: Research
        if session.current_stage == "research":
            from rich.prompt import Confirm as RConfirm
            if RConfirm.ask("LLM 리서치를 진행하시겠습니까?", default=True):
                console.print("\n[bold blue]LLM 리서치 중...[/]")
                from ppt_maker.wizard.research import run_research
                research_path = run_research(session)
                console.print(f"[green]리서치 완료:[/] {research_path}\n")
            else:
                console.print("[yellow]리서치를 건너뜁니다.[/]\n")
            session.advance_stage("review")
            save_session(session)

        # Stage 4: Review
        if session.current_stage == "review":
            console.print("[bold blue]섹션 리뷰[/]\n")
            from ppt_maker.wizard.review import run_review
            review_path = run_review(session)
            console.print(f"\n[green]리뷰 완료:[/] {review_path}\n")
            session.advance_stage("generate")
            save_session(session)

        # Stage 5: Generate PPTX
        if session.current_stage == "generate":
            from rich.prompt import Confirm as RConfirm
            if RConfirm.ask("PPTX를 생성하시겠습니까?", default=True):
                console.print("\n[bold blue]PPTX 생성 중...[/]")
                _wizard_generate(session)
            session.advance_stage("done")
            save_session(session)

        if session.current_stage == "done":
            console.print("\n[bold green]위저드 완료![/]")
            if session.pptx_path:
                pptx = session.get_output_path() / session.pptx_path
                console.print(f"  PPTX: {pptx}")
            if session.review_md:
                md = session.get_output_path() / session.review_md
                console.print(f"  마크다운: {md}")

    except PptMakerError as e:
        console.print(f"[bold red]오류:[/] {e}", err=True)
        if e.detail:
            console.print(f"[dim]{e.detail}[/]", err=True)
        raise typer.Exit(code=1) from e
    except KeyboardInterrupt:
        console.print("\n[yellow]중단됨. --resume 옵션으로 재개할 수 있습니다.[/]")
        raise typer.Exit(code=130) from None


def _wizard_collect(session: WizardSession) -> None:
    """Stage 1: 인터랙티브 정보 수집."""
    from rich.prompt import IntPrompt, Prompt

    session.topic = Prompt.ask("[bold]주제[/]")
    session.subtitle = Prompt.ask("부제 (선택)", default="")

    console.print("\n[dim]대상:[/] [1] 임원진  [2] 팀원  [3] 전사")
    audience_map = {"1": "executive", "2": "team", "3": "general"}
    audience_choice = Prompt.ask("대상", choices=["1", "2", "3"], default="2")
    session.audience = audience_map[audience_choice]

    console.print("[dim]목적:[/] [1] 보고  [2] 제안  [3] 교육  [4] 리뷰")
    purpose_map = {"1": "report", "2": "proposal", "3": "training", "4": "review"}
    purpose_choice = Prompt.ask("목적", choices=["1", "2", "3", "4"], default="1")
    session.purpose = purpose_map[purpose_choice]

    session.slide_count = IntPrompt.ask("슬라이드 수", default=8)

    console.print("[dim]톤:[/] [1] 비즈니스  [2] 기술적  [3] 캐주얼")
    tone_map = {"1": "professional", "2": "technical", "3": "casual"}
    tone_choice = Prompt.ask("톤", choices=["1", "2", "3"], default="1")
    session.tone = tone_map[tone_choice]

    console.print(f"\n[green]수집 완료:[/] {session.topic} ({session.audience}/{session.purpose})")


def _wizard_generate(session: WizardSession) -> None:
    """Stage 5: PPTX 생성 — 기존 pipeline 재사용."""
    from ppt_maker.config import TopicConfig
    from ppt_maker.pipeline import run_pipeline

    sections = session.get_sections()
    topic_config = TopicConfig(
        topic=session.topic,
        subtitle=session.subtitle,
        sections=sections,
        theme=session.theme,
        output_dir=Path(session.output_dir),
        font_family=session.font_family,
        use_research=False,  # 이미 리서치 완료됨
    )

    result = run_pipeline(topic_config)

    if result.pptx_path:
        session.pptx_path = result.pptx_path.name
        console.print(f"[green]PPTX 생성:[/] {result.pptx_path} ({result.slide_count}장)")


@app.command()
def preview(  # noqa: B008
    topic: str = typer.Argument(..., help="생성할 주제"),
    config: Path | None = typer.Option(None, "--config", "-c", help="TOML 설정 파일"),
    output_dir: Path = typer.Option(
        Path("./output"), "--output", "-o", help="출력 디렉토리",
    ),
) -> None:
    """마크다운 보고서만 생성합니다 (PPTX 변환 건너뜀)."""
    try:
        from ppt_maker.config import TopicConfig
        from ppt_maker.template.renderer import TemplateRenderer

        if config:
            topic_config = TopicConfig.from_toml(config)
        else:
            topic_config = TopicConfig(topic=topic, output_dir=output_dir)

        topic_config.output_dir.mkdir(parents=True, exist_ok=True)
        renderer = TemplateRenderer()
        report = renderer.render("base.md.j2", topic_config)

        md_path = topic_config.output_dir / "report.md"
        md_path.write_text(report.markdown, encoding="utf-8")

        console.print(f"[green]마크다운 미리보기 저장:[/] {md_path}")

    except PptMakerError as e:
        console.print(f"[bold red]오류:[/] {e}", err=True)
        raise typer.Exit(code=1) from e
