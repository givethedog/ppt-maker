"""에셋 매니저 — 로컬 에셋 + Simple Icons CDN 통합 조회.

조회 우선순위:
1. 로컬 에셋 디렉토리 (SVG/PNG)
2. Simple Icons CDN (SVG → PNG 변환)
3. 없으면 None (호출자가 텍스트 폴백 처리)
"""

from __future__ import annotations

import logging
from pathlib import Path

from ppt_maker.assets.converter import svg_to_png
from ppt_maker.assets.simple_icons import fetch_icon_svg, resolve_slug

logger = logging.getLogger(__name__)


class AssetManager:
    """로컬 + 리모트 에셋 통합 관리."""

    def __init__(
        self,
        local_dirs: list[Path] | None = None,
        icon_color: str = "white",
        icon_size: int = 256,
    ) -> None:
        self._local_dirs = local_dirs or []
        self._icon_color = icon_color
        self._icon_size = icon_size

    def find_brand_image(self, brand_name: str) -> Path | None:
        """브랜드 이미지를 찾아 PNG 경로를 반환.

        Args:
            brand_name: 브랜드 이름 (예: "BMW", "Mercedes-Benz", "n8n").

        Returns:
            PNG 파일 경로. 찾지 못하면 None.
        """
        key = brand_name.lower().strip()

        # 1. 로컬 에셋 검색
        for d in self._local_dirs:
            for ext in (".png", ".svg", ".jpg", ".jpeg"):
                # 정확한 이름 매칭
                candidate = d / f"{key}{ext}"
                if candidate.exists():
                    if ext == ".svg":
                        return svg_to_png(candidate, width=self._icon_size)
                    return candidate

            # slug 변환 후 재검색
            slug = resolve_slug(key)
            if slug and slug != key:
                for ext in (".png", ".svg", ".jpg", ".jpeg"):
                    candidate = d / f"{slug}{ext}"
                    if candidate.exists():
                        if ext == ".svg":
                            return svg_to_png(candidate, width=self._icon_size)
                        return candidate

        # 2. Simple Icons CDN
        slug = resolve_slug(key)
        if slug:
            svg_path = fetch_icon_svg(slug, color=self._icon_color)
            if svg_path:
                png_path = svg_path.with_suffix(".png")
                if not png_path.exists():
                    try:
                        svg_to_png(svg_path, png_path, width=self._icon_size)
                    except Exception as e:
                        logger.warning("SVG→PNG 변환 실패 (%s): %s", brand_name, e)
                        return None
                return png_path

        # 3. 찾지 못함
        logger.info("브랜드 이미지를 찾을 수 없습니다: %s", brand_name)
        return None

    def add_local_dir(self, path: Path) -> None:
        """로컬 에셋 디렉토리 추가."""
        path = Path(path)
        if path.is_dir() and path not in self._local_dirs:
            self._local_dirs.append(path)
            logger.info("로컬 에셋 디렉토리 추가: %s", path)
