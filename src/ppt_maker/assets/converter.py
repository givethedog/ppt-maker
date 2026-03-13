"""SVG → PNG 변환기.

python-pptx는 SVG를 직접 지원하지 않으므로, PNG로 변환하여 삽입합니다.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def svg_to_png(
    svg_path: Path,
    output_path: Path | None = None,
    width: int = 256,
    height: int | None = None,
) -> Path:
    """SVG 파일을 PNG로 변환.

    Args:
        svg_path: SVG 파일 경로.
        output_path: PNG 출력 경로. None이면 같은 디렉토리에 .png로 저장.
        width: 출력 너비 (px).
        height: 출력 높이 (px). None이면 비율 유지.

    Returns:
        생성된 PNG 파일 경로.
    """
    import cairosvg

    if output_path is None:
        output_path = svg_path.with_suffix(".png")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(output_path),
        output_width=width,
        output_height=height,
    )

    logger.info("SVG→PNG 변환: %s → %s (%dpx)", svg_path.name, output_path.name, width)
    return output_path
