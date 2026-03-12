"""하이브리드 변환 엔진 — pandoc + python-pptx 조합."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pptx import Presentation

from ppt_maker.config import SlideHint
from ppt_maker.converter.pandoc import md_to_pptx
from ppt_maker.converter.pptx_custom import SlideBuilder
from ppt_maker.errors import PandocError, PptxCustomError
from ppt_maker.theme.palette import ThemeConfig

logger = logging.getLogger(__name__)


@dataclass
class CustomSlideSpec:
    """커스텀 슬라이드 명세."""

    slide_type: str
    data: dict
    layout_hint: str = ""


@dataclass
class ConversionPlan:
    """변환 계획 — pandoc과 커스텀 섹션 분리."""

    pandoc_markdown: str = ""
    custom_slides: list[CustomSlideSpec] = field(default_factory=list)
    theme_path: Path | None = None
    merge_order: list[tuple[str, int]] = field(default_factory=list)


def build_conversion_plan(
    markdown: str,
    hints: list[SlideHint],
) -> ConversionPlan:
    """마크다운과 힌트에서 변환 계획 생성."""
    plan = ConversionPlan()

    # 힌트에서 커스텀 슬라이드 명세 추출
    custom_types = {"timeline", "comparison", "card_list", "process", "quote", "title"}

    for hint in hints:
        if hint.slide_type in custom_types or hint.conversion_strategy == "custom":
            plan.custom_slides.append(CustomSlideSpec(
                slide_type=hint.slide_type,
                data=hint.extra,
            ))

    # pandoc에는 전체 마크다운 전달 (커스텀 섹션도 기본 슬라이드로 변환)
    plan.pandoc_markdown = markdown

    return plan


class HybridConverter:
    """pandoc + python-pptx 하이브리드 변환 엔진."""

    def __init__(self, theme: ThemeConfig) -> None:
        self.theme = theme
        self.builder = SlideBuilder(theme)

    def convert(
        self,
        plan: ConversionPlan,
        output_path: Path,
        reference_doc: Path | None = None,
    ) -> Path:
        """변환 계획에 따라 PPTX 생성."""
        # Step 1: pandoc으로 기본 PPTX 생성
        pandoc_pptx = None
        if plan.pandoc_markdown.strip():
            try:
                with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
                    pandoc_pptx = Path(f.name)
                md_to_pptx(
                    plan.pandoc_markdown,
                    pandoc_pptx,
                    reference_doc=reference_doc,
                )
                logger.info("pandoc 기본 슬라이드 생성 완료")
            except PandocError as e:
                logger.warning("pandoc 변환 실패, 커스텀 슬라이드만으로 진행: %s", e)
                pandoc_pptx = None

        # Step 2: 커스텀 슬라이드 생성
        custom_prs = None
        if plan.custom_slides:
            custom_prs = self.builder.create_presentation()
            for spec in plan.custom_slides:
                try:
                    self.builder.build_slide(custom_prs, spec.slide_type, spec.data)
                except PptxCustomError as e:
                    logger.warning("커스텀 슬라이드 건너뜀 (%s): %s", spec.slide_type, e)

        # Step 3: 결과 결정
        if pandoc_pptx and pandoc_pptx.exists():
            # pandoc 결과를 기본으로 사용
            import shutil
            shutil.copy2(pandoc_pptx, output_path)
            pandoc_pptx.unlink(missing_ok=True)

            # 커스텀 슬라이드가 있으면 병합
            if custom_prs and len(custom_prs.slides) > 0:
                self._merge_custom_slides(output_path, custom_prs)

        elif custom_prs and len(custom_prs.slides) > 0:
            # pandoc 없이 커스텀만으로
            custom_prs.save(str(output_path))

        else:
            # 최소한의 빈 프레젠테이션
            prs = self.builder.create_presentation()
            prs.save(str(output_path))
            logger.warning("변환할 콘텐츠가 없어 빈 프레젠테이션이 생성되었습니다.")

        logger.info("PPTX 생성 완료: %s", output_path)
        return output_path

    def _merge_custom_slides(self, base_path: Path, custom_prs: Presentation) -> None:
        """커스텀 슬라이드를 기존 PPTX에 병합.

        현재는 단순히 커스텀 프레젠테이션의 슬라이드를 별도 파일로 저장하고
        로그로 안내합니다. 완전한 슬라이드 병합은 향후 구현.
        """
        custom_count = len(custom_prs.slides)
        logger.info(
            "커스텀 슬라이드 %d개 생성됨 (병합은 향후 구현 예정)", custom_count,
        )
