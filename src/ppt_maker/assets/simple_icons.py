"""Simple Icons CDN에서 브랜드 SVG 다운로드 + 로컬 캐시."""

from __future__ import annotations

import hashlib
import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

CDN_BASE = "https://cdn.simpleicons.org"
CACHE_DIR = Path.home() / ".cache" / "ppt-maker" / "icons"


def _cache_path(slug: str, color: str) -> Path:
    """캐시 파일 경로 생성."""
    key = hashlib.md5(f"{slug}_{color}".encode()).hexdigest()[:12]
    return CACHE_DIR / f"{slug}_{key}.svg"


def fetch_icon_svg(slug: str, color: str = "white") -> Path | None:
    """Simple Icons CDN에서 SVG를 다운로드하여 캐시에 저장.

    Args:
        slug: Simple Icons slug (예: "bmw", "mercedes", "porsche").
        color: SVG 색상 (예: "white", "00D2FF"). CDN이 색상을 적용.

    Returns:
        캐시된 SVG 파일 경로. 실패 시 None.
    """
    cached = _cache_path(slug, color)
    if cached.exists():
        logger.debug("캐시 히트: %s", cached)
        return cached

    url = f"{CDN_BASE}/{slug}/{color}"
    logger.info("Simple Icons 다운로드: %s", url)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ppt-maker/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                logger.warning("Simple Icons 응답 %d: %s", resp.status, slug)
                return None
            svg_data = resp.read()

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(svg_data)
        logger.info("캐시 저장: %s", cached)
        return cached

    except Exception as e:
        logger.warning("Simple Icons 다운로드 실패 (%s): %s", slug, e)
        return None


def clear_cache() -> int:
    """캐시 디렉토리를 정리. 삭제한 파일 수 반환."""
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.svg"):
        f.unlink()
        count += 1
    logger.info("아이콘 캐시 정리: %d개 삭제", count)
    return count


# 자동차 브랜드 슬러그 매핑 (자주 쓰는 것)
AUTO_BRAND_SLUGS: dict[str, str] = {
    "audi": "audi",
    "bmw": "bmw",
    "bentley": "bentley",
    "ferrari": "ferrari",
    "genesis": "genesis",
    "honda": "honda",
    "hyundai": "hyundai",
    "jaguar": "jaguar",
    "kia": "kia",
    "lamborghini": "lamborghini",
    "land rover": "landrover",
    "landrover": "landrover",
    "lexus": "lexus",
    "maserati": "maserati",
    "mazda": "mazda",
    "mercedes": "mercedes",
    "mercedes-benz": "mercedes",
    "mini": "mini",
    "nissan": "nissan",
    "porsche": "porsche",
    "rolls-royce": "rollsroyce",
    "rollsroyce": "rollsroyce",
    "tesla": "tesla",
    "toyota": "toyota",
    "volkswagen": "volkswagen",
    "volvo": "volvo",
    # 테크 브랜드 (IT 팀에서 자주 사용)
    "openai": "openai",
    "google": "google",
    "microsoft": "microsoft",
    "apple": "apple",
    "aws": "amazonwebservices",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "python": "python",
    "n8n": "n8n",
    "slack": "slack",
    "github": "github",
}


def resolve_slug(brand_name: str) -> str | None:
    """브랜드 이름을 Simple Icons slug로 변환."""
    key = brand_name.lower().strip()
    return AUTO_BRAND_SLUGS.get(key, key)
