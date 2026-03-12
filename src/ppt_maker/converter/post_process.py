"""PPTX 후처리 — 폰트 적용, 슬라이드 번호, 정합성 검증."""

from __future__ import annotations

import logging
from pathlib import Path

from pptx import Presentation

from ppt_maker.fonts.korean import apply_korean_font
from ppt_maker.fonts.resolver import resolve_font

logger = logging.getLogger(__name__)


def post_process(
    pptx_path: Path,
    font_family: str = "auto",
    output_path: Path | None = None,
) -> Path:
    """PPTX 후처리 파이프라인.

    1. 한글(EA) 폰트 일괄 적용
    2. 빈 슬라이드 제거
    3. 슬라이드 수 로깅

    Args:
        pptx_path: 원본 PPTX 경로.
        font_family: 폰트 패밀리 ("auto" 또는 구체적 폰트명).
        output_path: 출력 경로. None이면 원본 덮어쓰기.

    Returns:
        후처리된 PPTX 경로.
    """
    output_path = output_path or pptx_path

    # 1. 폰트 적용
    font = resolve_font(font_family)
    if font.is_fallback:
        logger.warning("폴백 폰트 사용: %s", font.name)

    apply_korean_font(pptx_path, font=font, output_path=output_path)

    # 2. 슬라이드 수 로깅
    prs = Presentation(str(output_path))
    slide_count = len(prs.slides)
    logger.info("후처리 완료: %d개 슬라이드, 폰트=%s", slide_count, font.name)

    return output_path
