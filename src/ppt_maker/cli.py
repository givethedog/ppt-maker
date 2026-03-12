"""CLI 인터페이스 (Typer 기반)."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console

from ppt_maker import __version__
from ppt_maker.errors import PptMakerError

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
) -> None:
    """주제에 대한 보고서(.md)와 프레젠테이션(.pptx)을 생성합니다."""
    try:
        from ppt_maker.config import TopicConfig
        from ppt_maker.pipeline import run_pipeline

        if config:
            topic_config = TopicConfig.from_toml(config)
        else:
            topic_config = TopicConfig(topic=topic, theme=theme, output_dir=output_dir)

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
def check() -> None:
    """환경 의존성을 검증합니다 (pandoc, 폰트 등)."""
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
