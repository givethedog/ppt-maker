"""python-pptx 커스텀 슬라이드 빌더.

구조화된 데이터에서 커스텀 슬라이드를 생성하는 빌더 패턴 구현.
create_slides.py의 헬퍼(set_bg, add_shape, add_text, add_bullet_list)를 리팩토링.
"""

from __future__ import annotations

import logging

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from ppt_maker.errors import PptxCustomError
from ppt_maker.theme.palette import ThemeConfig

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
    """커스텀 슬라이드 빌더."""

    def __init__(self, theme: ThemeConfig) -> None:
        self.theme = theme
        self.colors = theme.colors
        self.font_name = theme.fonts.heading

    def build_title(self, prs: Presentation, data: dict) -> None:
        """타이틀 슬라이드."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
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
        slide = prs.slides.add_slide(prs.slide_layouts[6])
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
        slide = prs.slides.add_slide(prs.slide_layouts[6])
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
        slide = prs.slides.add_slide(prs.slide_layouts[6])
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
        slide = prs.slides.add_slide(prs.slide_layouts[6])
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
        slide = prs.slides.add_slide(prs.slide_layouts[6])
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

    # --- 디스패처 ---

    BUILDERS: dict[str, str] = {
        "title": "build_title",
        "quote": "build_quote",
        "timeline": "build_timeline",
        "comparison": "build_comparison",
        "card_list": "build_card_list",
        "process": "build_process",
    }

    def build_slide(self, prs: Presentation, slide_type: str, data: dict) -> None:
        """슬라이드 타입에 따라 적절한 빌더 호출."""
        method_name = self.BUILDERS.get(slide_type)
        if method_name is None:
            raise PptxCustomError(
                f"지원되지 않는 슬라이드 타입: {slide_type}",
                detail=f"지원 타입: {', '.join(sorted(self.BUILDERS.keys()))}",
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

    def create_presentation(self) -> Presentation:
        """테마 설정이 적용된 빈 프레젠테이션 생성."""
        prs = Presentation()
        prs.slide_width = Emu(int(self.theme.slide.width * 914400))
        prs.slide_height = Emu(int(self.theme.slide.height * 914400))
        return prs
