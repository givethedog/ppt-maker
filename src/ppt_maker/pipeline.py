"""파이프라인 오케스트레이터 — 전체 생성 과정 조율."""

from __future__ import annotations

import copy
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

        # 2.5. 회사 템플릿 로드
        from ppt_maker.workspace import (
            get_registered_template,
            get_template_manifest_path,
        )

        company_template = get_registered_template()
        layout_mapping: dict[str, int] = {}
        if company_template:
            console.print(
                f"[bold blue]회사 템플릿:[/] {company_template.name}"
            )
            manifest_path = get_template_manifest_path()
            if manifest_path:
                from ppt_maker.template.analyzer import load_manifest

                manifest = load_manifest(manifest_path)
                layout_mapping = manifest.layout_mapping
            else:
                console.print(
                    "[yellow]매니페스트 없음 — "
                    "ppt-maker init --template 으로 재등록하세요[/]"
                )

        # 2.9 LLM 콘텐츠 생성 (research)
        research_sections: list = []
        if config.use_research and not config.sections:
            console.print("[bold blue]LLM 콘텐츠 생성 중...[/]")
            from ppt_maker.research.generator import ContentGenerator
            from ppt_maker.research.llm import LLMConfig

            llm_config = LLMConfig(
                api_base=config.llm_api_base,
                model=config.llm_model,
                api_key_env=config.llm_api_key_env,
            )
            generator = ContentGenerator(llm_config)
            generated = generator.generate(
                topic=config.topic,
                subtitle=config.subtitle,
            )
            research_sections = generated.sections
            console.print(f"[green]LLM 생성 완료:[/] {len(research_sections)}개 섹션")

        # 최종 섹션: 기존 설정 우선, 없으면 LLM 생성 결과 사용
        effective_sections = config.sections or research_sections

        # 3. 템플릿 렌더링 (config 원본을 변경하지 않기 위해 복사본 사용)
        console.print("[bold blue]마크다운 렌더링 중...[/]")
        render_config = copy.copy(config)
        render_config.sections = effective_sections
        renderer = TemplateRenderer()
        report: RenderedReport = renderer.render("base.md.j2", render_config)

        # 4. 마크다운 저장
        md_path = config.output_dir / "report.md"
        md_path.write_text(report.markdown, encoding="utf-8")
        result.markdown_path = md_path
        console.print(f"[green]마크다운 저장:[/] {md_path}")

        # 5. 변환 계획
        plan = build_conversion_plan(report.markdown, report.slide_hints)

        # 5.5. 에셋 매니저 생성
        from ppt_maker.assets.manager import AssetManager

        asset_dirs = []
        assets_dir = Path("assets")
        if assets_dir.is_dir():
            asset_dirs.append(assets_dir)
        output_assets = config.output_dir / "assets"
        if output_assets.is_dir():
            asset_dirs.append(output_assets)
        asset_manager = AssetManager(local_dirs=asset_dirs)

        # 6. PPTX 변환
        console.print("[bold blue]PPTX 변환 중...[/]")
        pptx_path = config.output_dir / "report.pptx"
        converter = HybridConverter(
            theme,
            layout_mapping=layout_mapping,
            template_path=company_template,
            asset_manager=asset_manager,
        )
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
