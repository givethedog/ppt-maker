"""파이프라인 오케스트레이터 — 전체 생성 과정 조율."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from ppt_maker.config import TopicConfig
from ppt_maker.converter.hybrid import HybridConverter, build_conversion_plan
from ppt_maker.converter.post_process import post_process
from ppt_maker.errors import PipelineError, PptMakerError
from ppt_maker.template.renderer import RenderedReport, TemplateRenderer
from ppt_maker.theme.manager import ThemeManager

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class PipelineResult:
    """파이프라인 실행 결과."""

    markdown_path: Path | None = None
    pptx_path: Path | None = None
    slide_count: int = 0
    elapsed_seconds: float = 0.0
    warnings: list[str] = field(default_factory=list)


def run_pipeline(config: TopicConfig) -> PipelineResult:
    """전체 파이프라인 실행.

    config 로드 → 템플릿 렌더링 → 변환 → 후처리 → 출력.
    """
    start = time.monotonic()
    result = PipelineResult()

    try:
        # 1. 출력 디렉토리 생성
        config.output_dir.mkdir(parents=True, exist_ok=True)

        # 2. 테마 로드
        console.print(f"[bold blue]테마 로드:[/] {config.theme}")
        tm = ThemeManager()
        theme = tm.load_theme(config.theme)
        reference_doc = tm.get_reference_pptx(config.theme)

        # 3. 템플릿 렌더링
        console.print("[bold blue]마크다운 렌더링 중...[/]")
        renderer = TemplateRenderer()
        report: RenderedReport = renderer.render("base.md.j2", config)

        # 4. 마크다운 저장
        md_path = config.output_dir / "report.md"
        md_path.write_text(report.markdown, encoding="utf-8")
        result.markdown_path = md_path
        console.print(f"[green]마크다운 저장:[/] {md_path}")

        # 5. 변환 계획
        plan = build_conversion_plan(report.markdown, report.slide_hints)

        # 6. PPTX 변환
        console.print("[bold blue]PPTX 변환 중...[/]")
        pptx_path = config.output_dir / "report.pptx"
        converter = HybridConverter(theme)
        converter.convert(plan, pptx_path, reference_doc=reference_doc)

        # 7. 후처리 (폰트 적용)
        console.print("[bold blue]후처리 중...[/]")
        post_process(pptx_path, font_family=config.font_family)
        result.pptx_path = pptx_path

        # 8. 결과 집계
        from pptx import Presentation

        prs = Presentation(str(pptx_path))
        result.slide_count = len(prs.slides)

    except PptMakerError:
        raise
    except Exception as e:
        raise PipelineError(
            f"파이프라인 실행 중 예상치 못한 오류: {e}",
        ) from e
    finally:
        result.elapsed_seconds = time.monotonic() - start

    return result
