"""하이브리드 변환 엔진 — pandoc + python-pptx 조합."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pptx import Presentation

from ppt_maker.config import SlideHint
from ppt_maker.converter.pandoc import md_to_pptx
from ppt_maker.converter.pptx_custom import SlideBuilder
from ppt_maker.errors import PandocError, PptxCustomError
from ppt_maker.theme.palette import ThemeConfig

if TYPE_CHECKING:
    from ppt_maker.assets.manager import AssetManager

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


def _parse_markdown_sections(markdown: str) -> list[dict]:
    """마크다운을 섹션 단위로 분리하여 제목과 콘텐츠를 추출."""
    sections: list[dict] = []
    current: dict | None = None

    for line in markdown.split("\n"):
        if line.startswith("## "):
            if current:
                current["content"] = current["content"].strip()
                sections.append(current)
            current = {"title": line[3:].strip(), "content": "", "index": len(sections) + 1}
        elif current:
            # slide hint 주석은 content에 포함하지 않음
            if not line.strip().startswith("<!-- slide:"):
                current["content"] += line + "\n"

    if current:
        current["content"] = current["content"].strip()
        sections.append(current)

    return sections


def _content_to_items(content: str) -> list[str]:
    """마크다운 콘텐츠를 프레젠테이션 항목 리스트로 변환.

    불릿 라인뿐 아니라 의미 있는 비불릿 단락도 항목으로 포함하여
    콘텐츠 유실을 방지합니다.
    """
    items: list[str] = []
    # 테이블/구분선 등 프레젠테이션에 부적절한 라인 건너뛰기
    skip_prefixes = ("|", "---", "```")
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(skip_prefixes):
            continue
        # 불릿 라인
        if stripped.startswith(("- ", "* ", "• ")):
            items.append(stripped[2:].strip())
        # 번호 매기기 라인
        elif stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            items.append(stripped.split(".", 1)[1].strip() if "." in stripped else stripped)
        # 의미 있는 비불릿 단락 (빈 줄, 마크다운 문법 제외)
        else:
            items.append(stripped)
    return items


def build_conversion_plan(
    markdown: str,
    hints: list[SlideHint],
) -> ConversionPlan:
    """마크다운과 힌트에서 변환 계획 생성."""
    plan = ConversionPlan()

    # 마크다운 섹션 파싱
    md_sections = _parse_markdown_sections(markdown)

    # 힌트를 section_index로 매핑
    hint_map: dict[int, SlideHint] = {}
    for hint in hints:
        hint_map[hint.section_index] = hint

    # H1 제목과 부제 추출 (title 슬라이드용, section_index=0)
    h1_title = ""
    h1_subtitle = ""
    for line in markdown.split("\n"):
        if line.startswith("# ") and not line.startswith("## "):
            h1_title = line[2:].strip()
        elif line.startswith("> ") and h1_title and not h1_subtitle:
            h1_subtitle = line[2:].strip()

    # 모든 힌트에 대해 커스텀 슬라이드 명세 생성 (콘텐츠 포함)
    for hint in hints:
        idx = hint.section_index
        # 매칭되는 마크다운 섹션 찾기
        md_section = md_sections[idx - 1] if 0 < idx <= len(md_sections) else None

        data = dict(hint.extra)
        if idx == 0 and hint.slide_type == "title":
            # 자동 생성 타이틀: H1에서 제목/부제 추출
            data.setdefault("title", h1_title)
            data.setdefault("subtitle", h1_subtitle)
        elif md_section:
            data.setdefault("title", md_section["title"])
            data.setdefault("content", md_section["content"])
            items = _content_to_items(md_section["content"])
            if items:
                data.setdefault("items", items)

        plan.custom_slides.append(CustomSlideSpec(
            slide_type=hint.slide_type,
            data=data,
        ))

    # pandoc에는 전체 마크다운 전달 (커스텀 섹션도 기본 슬라이드로 변환)
    plan.pandoc_markdown = markdown

    return plan


class HybridConverter:
    """pandoc + python-pptx 하이브리드 변환 엔진."""

    def __init__(
        self,
        theme: ThemeConfig,
        layout_mapping: dict[str, int] | None = None,
        template_path: Path | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self.theme = theme
        self.template_path = template_path
        self.builder = SlideBuilder(
            theme,
            layout_mapping=layout_mapping,
            asset_manager=asset_manager,
        )

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

        # 회사 템플릿이 있으면 reference_doc으로도 사용
        if reference_doc is None and self.template_path:
            reference_doc = self.template_path

        # Step 2: 커스텀 슬라이드 생성
        custom_prs = None
        if plan.custom_slides:
            custom_prs = self.builder.create_presentation(
                template_path=self.template_path,
            )
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
            if plan.custom_slides:
                self._append_custom_slides(output_path, plan.custom_slides)

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

    def _append_custom_slides(
        self, base_path: Path, custom_specs: list[CustomSlideSpec],
    ) -> None:
        """커스텀 슬라이드를 기존 PPTX에 직접 추가.

        pandoc이 생성한 프레젠테이션을 열어서, 같은 파일 안에
        커스텀 슬라이드를 SlideBuilder로 직접 빌드합니다.
        """
        prs = Presentation(str(base_path))
        added = 0
        for spec in custom_specs:
            try:
                self.builder.build_slide(prs, spec.slide_type, spec.data)
                added += 1
            except PptxCustomError as e:
                logger.warning(
                    "커스텀 슬라이드 병합 건너뜀 (%s): %s",
                    spec.slide_type, e,
                )
        if added:
            prs.save(str(base_path))
            logger.info("커스텀 슬라이드 %d개를 기존 PPTX에 병합 완료", added)
