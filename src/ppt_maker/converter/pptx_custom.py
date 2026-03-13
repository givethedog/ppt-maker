"""python-pptx 커스텀 슬라이드 빌더.

구조화된 데이터에서 커스텀 슬라이드를 생성하는 빌더 패턴 구현.
create_slides.py의 헬퍼(set_bg, add_shape, add_text, add_bullet_list)를 리팩토링.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from ppt_maker.errors import PptxCustomError
from ppt_maker.theme.palette import ThemeConfig

if TYPE_CHECKING:
    from ppt_maker.assets.manager import AssetManager

logger = logging.getLogger(__name__)

# 슬라이드 크기 기본값 (16:9)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)


# --- 헬퍼 함수 (create_slides.py에서 리팩토링) ---


def set_bg(slide, color: RGBColor) -> None:
    """슬라이드 배경색 설정."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(
    slide,
    left: int | float,
    top: int | float,
    width: int | float,
    height: int | float,
    fill_color: RGBColor | None = None,
    border_color: RGBColor | None = None,
    border_width: int = 0,
) -> object:
    """사각형 도형 추가."""
    from pptx.enum.shapes import MSO_SHAPE

    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()

    if border_color and border_width:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()

    return shape


def add_text(
    slide,
    text: str,
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    font_size: int = 18,
    font_color: RGBColor = RGBColor(0xFF, 0xFF, 0xFF),
    font_name: str = "Apple SD Gothic Neo",
    bold: bool = False,
    alignment: PP_ALIGN = PP_ALIGN.LEFT,
) -> object:
    """텍스트 상자 추가."""
    tx_box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    tf = tx_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.name = font_name
    p.font.bold = bold
    p.alignment = alignment
    return tx_box


def add_bullet_list(
    slide,
    items: list[str],
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    font_size: int = 16,
    font_color: RGBColor = RGBColor(0xFF, 0xFF, 0xFF),
    font_name: str = "Apple SD Gothic Neo",
    bullet_color: RGBColor | None = None,
) -> object:
    """불릿 리스트 텍스트 상자 추가."""
    tx_box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    tf = tx_box.text_frame
    tf.word_wrap = True

    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(font_size)
        p.font.color.rgb = font_color
        p.font.name = font_name
        p.space_after = Pt(6)

    return tx_box


# --- 슬라이드 타입별 빌더 ---


class SlideBuilder:
    """커스텀 슬라이드 빌더.

    회사 템플릿이 등록되어 있으면 해당 레이아웃을 사용하고,
    없으면 기본 Blank 레이아웃에 도형을 직접 배치합니다.
    """

    def __init__(
        self,
        theme: ThemeConfig,
        layout_mapping: dict[str, int] | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self.theme = theme
        self.colors = theme.colors
        self.font_name = theme.fonts.heading
        self._layout_mapping = layout_mapping or {}
        self.asset_manager = asset_manager

    def _get_layout(self, prs: Presentation, slide_type: str) -> object:
        """슬라이드 타입에 매핑된 레이아웃 반환. 없으면 Blank."""
        idx = self._layout_mapping.get(slide_type)
        if idx is not None and idx < len(prs.slide_layouts):
            return prs.slide_layouts[idx]
        # Blank 레이아웃 폴백 (마지막 또는 인덱스 6)
        blank_idx = self._layout_mapping.get("blank")
        if blank_idx is not None and blank_idx < len(prs.slide_layouts):
            return prs.slide_layouts[blank_idx]
        fallback = min(6, len(prs.slide_layouts) - 1)
        return prs.slide_layouts[fallback]

    def _add_slide(self, prs: Presentation, slide_type: str) -> object:
        """레이아웃 매핑 기반 슬라이드 추가."""
        layout = self._get_layout(prs, slide_type)
        return prs.slides.add_slide(layout)

    def build_title(self, prs: Presentation, data: dict) -> None:
        """타이틀 슬라이드."""
        slide = self._add_slide(prs, "title")
        set_bg(slide, self.colors.bg_primary)

        add_text(
            slide, data.get("title", ""),
            1.0, 2.0, 11.0, 1.5,
            font_size=40, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
            alignment=PP_ALIGN.CENTER,
        )
        if data.get("subtitle"):
            add_text(
                slide, data["subtitle"],
                1.0, 3.8, 11.0, 1.0,
                font_size=24, font_color=self.colors.accent,
                font_name=self.font_name,
                alignment=PP_ALIGN.CENTER,
            )
        if data.get("date"):
            add_text(
                slide, data["date"],
                1.0, 5.5, 11.0, 0.5,
                font_size=16, font_color=self.colors.text_secondary,
                font_name=self.font_name,
                alignment=PP_ALIGN.CENTER,
            )

    def build_quote(self, prs: Presentation, data: dict) -> None:
        """인용/질문 슬라이드."""
        slide = self._add_slide(prs, "keynote")
        set_bg(slide, self.colors.bg_primary)

        # 인용 부호
        add_text(
            slide, '"',
            1.0, 1.0, 1.0, 1.5,
            font_size=72, font_color=self.colors.accent,
            font_name=self.font_name, bold=True,
        )
        add_text(
            slide, data.get("quote", ""),
            1.5, 2.5, 10.0, 2.0,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name,
            alignment=PP_ALIGN.CENTER,
        )
        if data.get("attribution"):
            add_text(
                slide, f"— {data['attribution']}",
                1.5, 5.0, 10.0, 0.5,
                font_size=16, font_color=self.colors.text_secondary,
                font_name=self.font_name,
                alignment=PP_ALIGN.RIGHT,
            )

    def build_timeline(self, prs: Presentation, data: dict) -> None:
        """타임라인 슬라이드."""
        slide = self._add_slide(prs, "three_content")
        set_bg(slide, self.colors.bg_primary)

        title = data.get("title", "타임라인")
        add_text(
            slide, title,
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        events = data.get("events", [])
        if not events:
            return

        # 타임라인 라인
        add_shape(slide, 1.0, 3.5, 11.0, 0.03, fill_color=self.colors.accent)

        accent_colors = [self.colors.accent, self.colors.accent2, self.colors.accent3]
        spacing = min(11.0 / max(len(events), 1), 3.0)

        for i, event in enumerate(events):
            x = 1.0 + i * spacing
            color = event.get("color") or accent_colors[i % len(accent_colors)]
            if isinstance(color, str):
                from ppt_maker.theme.palette import hex_to_rgb
                color = hex_to_rgb(color)

            # 이벤트 점
            add_shape(slide, x + spacing / 2 - 0.1, 3.35, 0.2, 0.2, fill_color=color)
            # 날짜
            add_text(
                slide, event.get("date", ""),
                x, 2.3, spacing, 0.5,
                font_size=12, font_color=self.colors.accent,
                font_name=self.font_name, alignment=PP_ALIGN.CENTER,
            )
            # 제목
            add_text(
                slide, event.get("title", ""),
                x, 4.0, spacing, 1.0,
                font_size=14, font_color=self.colors.text_primary,
                font_name=self.font_name, alignment=PP_ALIGN.CENTER,
            )

    def build_comparison(self, prs: Presentation, data: dict) -> None:
        """좌우 비교 슬라이드."""
        slide = self._add_slide(prs, "comparison")
        set_bg(slide, self.colors.bg_primary)

        title = data.get("title", "비교")
        add_text(
            slide, title,
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        left = data.get("left", {})
        right = data.get("right", {})

        # 좌측
        add_shape(slide, 0.5, 1.5, 5.8, 5.5, fill_color=self.colors.bg_secondary)
        add_text(
            slide, left.get("title", ""),
            0.8, 1.7, 5.2, 0.6,
            font_size=22, font_color=self.colors.accent,
            font_name=self.font_name, bold=True,
        )
        if left.get("items"):
            add_bullet_list(
                slide, left["items"],
                0.8, 2.5, 5.2, 4.0,
                font_color=self.colors.text_primary,
                font_name=self.font_name,
            )

        # 우측
        add_shape(slide, 6.8, 1.5, 5.8, 5.5, fill_color=self.colors.bg_secondary)
        add_text(
            slide, right.get("title", ""),
            7.1, 1.7, 5.2, 0.6,
            font_size=22, font_color=self.colors.accent2,
            font_name=self.font_name, bold=True,
        )
        if right.get("items"):
            add_bullet_list(
                slide, right["items"],
                7.1, 2.5, 5.2, 4.0,
                font_color=self.colors.text_primary,
                font_name=self.font_name,
            )

    def build_card_list(self, prs: Presentation, data: dict) -> None:
        """카드형 목록 슬라이드."""
        slide = self._add_slide(prs, "grid_2x2")
        set_bg(slide, self.colors.bg_primary)

        title = data.get("title", "")
        add_text(
            slide, title,
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        items = data.get("items", [])
        accent_colors = [self.colors.accent, self.colors.accent2, self.colors.accent3]

        for i, item in enumerate(items[:6]):
            col = i % 3
            row = i // 3
            x = 0.5 + col * 4.2
            y = 1.5 + row * 3.0

            add_shape(slide, x, y, 3.8, 2.5, fill_color=self.colors.bg_secondary)
            add_text(
                slide, item.get("title", ""),
                x + 0.2, y + 0.2, 3.4, 0.5,
                font_size=18, font_color=accent_colors[i % len(accent_colors)],
                font_name=self.font_name, bold=True,
            )
            if item.get("detail"):
                add_text(
                    slide, item["detail"],
                    x + 0.2, y + 0.8, 3.4, 1.5,
                    font_size=14, font_color=self.colors.text_primary,
                    font_name=self.font_name,
                )

    def build_process(self, prs: Presentation, data: dict) -> None:
        """단계별 프로세스 슬라이드."""
        slide = self._add_slide(prs, "grid_3")
        set_bg(slide, self.colors.bg_primary)

        title = data.get("title", "프로세스")
        add_text(
            slide, title,
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        steps = data.get("steps", [])
        accent_colors = [self.colors.accent, self.colors.accent2, self.colors.accent3]
        n = len(steps)
        if n == 0:
            return

        step_width = min(12.0 / n, 3.0)
        start_x = (13.333 - step_width * n) / 2

        for i, step in enumerate(steps):
            x = start_x + i * step_width
            color = accent_colors[i % len(accent_colors)]

            # 단계 번호 원
            add_shape(slide, x + step_width / 2 - 0.3, 2.0, 0.6, 0.6, fill_color=color)
            add_text(
                slide, str(i + 1),
                x + step_width / 2 - 0.3, 2.05, 0.6, 0.6,
                font_size=20, font_color=self.colors.bg_primary,
                font_name=self.font_name, bold=True,
                alignment=PP_ALIGN.CENTER,
            )
            # 라벨
            add_text(
                slide, step.get("label", ""),
                x, 2.8, step_width, 0.5,
                font_size=16, font_color=self.colors.text_primary,
                font_name=self.font_name, bold=True,
                alignment=PP_ALIGN.CENTER,
            )
            # 설명
            if step.get("desc"):
                add_text(
                    slide, step["desc"],
                    x, 3.4, step_width, 2.0,
                    font_size=12, font_color=self.colors.text_secondary,
                    font_name=self.font_name,
                    alignment=PP_ALIGN.CENTER,
                )

            # 화살표 (마지막 제외)
            if i < n - 1:
                add_text(
                    slide, "→",
                    x + step_width - 0.2, 2.1, 0.4, 0.5,
                    font_size=24, font_color=self.colors.text_secondary,
                    font_name=self.font_name,
                    alignment=PP_ALIGN.CENTER,
                )

    def build_section(self, prs: Presentation, data: dict) -> None:
        """섹션 구분 슬라이드."""
        slide = self._add_slide(prs, "section")
        set_bg(slide, self.colors.bg_primary)

        add_text(
            slide, data.get("title", ""),
            1.0, 2.5, 11.0, 1.5,
            font_size=36, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
            alignment=PP_ALIGN.LEFT,
        )
        if data.get("subtitle"):
            add_text(
                slide, data["subtitle"],
                1.0, 4.2, 11.0, 1.0,
                font_size=20, font_color=self.colors.text_secondary,
                font_name=self.font_name,
                alignment=PP_ALIGN.LEFT,
            )

    def build_picture_left(self, prs: Presentation, data: dict) -> None:
        """좌측 이미지 + 우측 텍스트 슬라이드."""
        slide = self._add_slide(prs, "picture_left")
        set_bg(slide, self.colors.bg_primary)

        add_text(
            slide, data.get("title", ""),
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        # 좌측 이미지 영역 — asset_manager가 있으면 실제 이미지 삽입
        brand_name = data.get("brand", data.get("image", ""))
        image_path: Path | None = None
        if self.asset_manager and brand_name:
            image_path = self.asset_manager.find_brand_image(brand_name)

        if image_path and image_path.exists():
            slide.shapes.add_picture(
                str(image_path),
                Inches(0.5), Inches(1.5), Inches(4.5), Inches(5.0),
            )
        else:
            # 폴백: 색상 사각형 플레이스홀더
            add_shape(
                slide, 0.5, 1.5, 5.5, 5.5,
                fill_color=self.colors.bg_secondary,
            )
            add_text(
                slide, data.get("image_label", "[이미지]"),
                1.5, 3.5, 3.5, 1.0,
                font_size=16, font_color=self.colors.text_secondary,
                font_name=self.font_name,
                alignment=PP_ALIGN.CENTER,
            )

        # 우측 텍스트
        if data.get("content"):
            add_text(
                slide, data["content"],
                6.5, 1.8, 6.0, 5.0,
                font_size=16, font_color=self.colors.text_primary,
                font_name=self.font_name,
            )
        if data.get("items"):
            add_bullet_list(
                slide, data["items"],
                6.5, 1.8, 6.0, 5.0,
                font_color=self.colors.text_primary,
                font_name=self.font_name,
            )

    def build_picture_right(self, prs: Presentation, data: dict) -> None:
        """좌측 텍스트 + 우측 이미지 슬라이드."""
        slide = self._add_slide(prs, "picture_right")
        set_bg(slide, self.colors.bg_primary)

        add_text(
            slide, data.get("title", ""),
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        # 좌측 텍스트
        if data.get("content"):
            add_text(
                slide, data["content"],
                0.5, 1.8, 6.0, 5.0,
                font_size=16, font_color=self.colors.text_primary,
                font_name=self.font_name,
            )
        if data.get("items"):
            add_bullet_list(
                slide, data["items"],
                0.5, 1.8, 6.0, 5.0,
                font_color=self.colors.text_primary,
                font_name=self.font_name,
            )

        # 우측 이미지 영역 — asset_manager가 있으면 실제 이미지 삽입
        brand_name = data.get("brand", data.get("image", ""))
        image_path: Path | None = None
        if self.asset_manager and brand_name:
            image_path = self.asset_manager.find_brand_image(brand_name)

        if image_path and image_path.exists():
            slide.shapes.add_picture(
                str(image_path),
                Inches(8.0), Inches(1.5), Inches(4.5), Inches(5.0),
            )
        else:
            # 폴백: 색상 사각형 플레이스홀더
            add_shape(
                slide, 7.0, 1.5, 5.5, 5.5,
                fill_color=self.colors.bg_secondary,
            )
            add_text(
                slide, data.get("image_label", "[이미지]"),
                8.0, 3.5, 3.5, 1.0,
                font_size=16, font_color=self.colors.text_secondary,
                font_name=self.font_name,
                alignment=PP_ALIGN.CENTER,
            )

    def build_blank(self, prs: Presentation, data: dict) -> None:
        """빈 콘텐츠 영역 슬라이드 (밝은 배경)."""
        slide = self._add_slide(prs, "content_area")
        if data.get("title"):
            add_text(
                slide, data["title"],
                0.5, 0.3, 12.0, 0.8,
                font_size=28, font_color=self.colors.text_primary,
                font_name=self.font_name, bold=True,
            )

    def build_blank_dark(self, prs: Presentation, data: dict) -> None:
        """빈 콘텐츠 영역 슬라이드 (어두운 배경)."""
        slide = self._add_slide(prs, "content_area_dark")
        set_bg(slide, self.colors.bg_primary)
        if data.get("title"):
            add_text(
                slide, data["title"],
                0.5, 0.3, 12.0, 0.8,
                font_size=28, font_color=self.colors.text_primary,
                font_name=self.font_name, bold=True,
            )

    def build_keynote(self, prs: Presentation, data: dict) -> None:
        """키노트 슬라이드 — 이미지 + 핵심 메시지."""
        slide = self._add_slide(prs, "keynote")
        set_bg(slide, self.colors.bg_primary)

        add_text(
            slide, data.get("title", ""),
            1.0, 2.0, 11.0, 2.0,
            font_size=36, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
            alignment=PP_ALIGN.CENTER,
        )
        if data.get("message"):
            add_text(
                slide, data["message"],
                1.5, 4.5, 10.0, 1.5,
                font_size=20, font_color=self.colors.text_secondary,
                font_name=self.font_name,
                alignment=PP_ALIGN.CENTER,
            )

    def build_content(self, prs: Presentation, data: dict) -> None:
        """일반 콘텐츠 슬라이드 — 제목 + 불릿 리스트."""
        slide = self._add_slide(prs, "content")
        set_bg(slide, self.colors.bg_primary)

        add_text(
            slide, data.get("title", ""),
            0.5, 0.3, 12.0, 0.8,
            font_size=28, font_color=self.colors.text_primary,
            font_name=self.font_name, bold=True,
        )

        items = data.get("items", [])
        if items:
            add_bullet_list(
                slide, items,
                0.8, 1.5, 11.5, 5.5,
                font_size=16, font_color=self.colors.text_primary,
                font_name=self.font_name,
            )
        elif data.get("content"):
            add_text(
                slide, data["content"],
                0.8, 1.5, 11.5, 5.5,
                font_size=16, font_color=self.colors.text_primary,
                font_name=self.font_name,
            )

    # --- 디스패처 ---

    BUILDERS: dict[str, str] = {
        "title": "build_title",
        "section": "build_section",
        "content": "build_content",
        "quote": "build_quote",
        "timeline": "build_timeline",
        "comparison": "build_comparison",
        "card_list": "build_card_list",
        "process": "build_process",
        "picture_left": "build_picture_left",
        "picture_right": "build_picture_right",
        "blank": "build_blank",
        "blank_dark": "build_blank_dark",
        "keynote": "build_keynote",
    }

    def build_slide(self, prs: Presentation, slide_type: str, data: dict) -> None:
        """슬라이드 타입에 따라 적절한 빌더 호출."""
        method_name = self.BUILDERS.get(slide_type)
        if method_name is None:
            raise PptxCustomError(
                f"지원되지 않는 슬라이드 타입: {slide_type}",
                detail=f"지원 타입: {', '.join(sorted(self.BUILDERS))}",
            )
        method = getattr(self, method_name)
        try:
            method(prs, data)
        except PptxCustomError:
            raise
        except Exception as e:
            raise PptxCustomError(
                f"슬라이드 생성 실패 ({slide_type}): {e}",
            ) from e

    def create_presentation(
        self,
        template_path: Path | None = None,
    ) -> Presentation:
        """프레젠테이션 생성. 회사 템플릿이 있으면 해당 파일 기반."""
        if template_path and template_path.exists():
            prs = Presentation(str(template_path))
            # 기존 가이드 슬라이드 제거 (빈 프레젠테이션으로 시작)
            # lxml element를 직접 조작하여 XML 트리 정합성 보장
            xml_slides = prs.slides._sldIdLst
            for slide_id in list(xml_slides):
                rel_id = slide_id.get(
                    "{http://schemas.openxmlformats.org/officeDocument"
                    "/2006/relationships}id"
                )
                if rel_id:
                    prs.part.drop_rel(rel_id)
                xml_slides.remove(slide_id)
            logger.info("회사 템플릿 기반 프레젠테이션 생성: %s", template_path)
            return prs
        prs = Presentation()
        prs.slide_width = Emu(int(self.theme.slide.width * 914400))
        prs.slide_height = Emu(int(self.theme.slide.height * 914400))
        return prs
