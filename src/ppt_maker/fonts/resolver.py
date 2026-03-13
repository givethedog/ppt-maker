"""OS별 폰트 탐색기.

macOS/Linux/Windows에서 시스템 폰트를 탐색하고, 한글 폰트 폴백 체인을 구현합니다.
"""

from __future__ import annotations

import logging
import platform
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# OS별 기본 한글 폰트 및 폴백 체인
# BMWGroupTN Condensed: BMW CI 폰트 (회사 템플릿 사용 시 우선)
KOREAN_FONT_CHAINS: dict[str, list[str]] = {
    "Darwin": [
        "BMWGroupTN Condensed", "Apple SD Gothic Neo",
        "Noto Sans KR", "AppleGothic",
    ],
    "Linux": [
        "BMWGroupTN Condensed", "Noto Sans KR",
        "NanumGothic", "UnDotum",
    ],
    "Windows": [
        "BMWGroupTN Condensed", "Malgun Gothic",
        "NanumGothic", "Gulim",
    ],
}

# 일반 폴백 (한글 폰트를 하나도 못 찾을 때)
UNIVERSAL_FALLBACK = "Arial"


@dataclass(frozen=True)
class ResolvedFont:
    """탐색 결과 폰트 정보."""

    name: str
    is_fallback: bool = False


def _get_os_name() -> str:
    return platform.system()


def _font_exists_macos(font_name: str) -> bool:
    """macOS: system_profiler 또는 fc-list으로 폰트 존재 확인."""
    try:
        result = subprocess.run(
            ["fc-list", f":family={font_name}"],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip():
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # fc-list 없으면 mdfind 시도
    try:
        result = subprocess.run(
            ["mdfind", "-name", f"{font_name}.ttf"],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip():
            return True
        for ext in (".ttc", ".otf"):
            result = subprocess.run(
                ["mdfind", "-name", f"{font_name}{ext}"],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout.strip():
                return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _font_exists_linux(font_name: str) -> bool:
    """Linux: fc-list으로 폰트 존재 확인."""
    try:
        result = subprocess.run(
            ["fc-list", f":family={font_name}"],
            capture_output=True, text=True, timeout=10,
        )
        return bool(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _font_exists_windows(font_name: str) -> bool:
    """Windows: 레지스트리에서 폰트 확인."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
        )
        i = 0
        while True:
            try:
                name, _, _ = winreg.EnumValue(key, i)
                if font_name.lower() in name.lower():
                    return True
                i += 1
            except OSError:
                break
        return False
    except Exception:
        return False


def font_exists(font_name: str) -> bool:
    """현재 OS에서 지정된 폰트가 존재하는지 확인."""
    os_name = _get_os_name()
    checkers = {
        "Darwin": _font_exists_macos,
        "Linux": _font_exists_linux,
        "Windows": _font_exists_windows,
    }
    checker = checkers.get(os_name)
    if checker is None:
        logger.warning("지원되지 않는 OS: %s — 폰트 검증을 건너뜁니다.", os_name)
        return True  # 알 수 없는 OS에서는 존재한다고 가정
    return checker(font_name)


def resolve_font(
    font_family: str = "auto",
    fallback_chain: list[str] | None = None,
) -> ResolvedFont:
    """폰트를 탐색하여 사용 가능한 폰트를 반환.

    Args:
        font_family: 원하는 폰트 이름. "auto"면 OS 기본 한글 폰트.
        fallback_chain: 추가 폴백 체인. None이면 OS 기본 체인 사용.

    Returns:
        ResolvedFont: 탐색된 폰트 정보.

    Raises:
        FontError: 사용 가능한 폰트를 하나도 찾지 못한 경우.
    """
    os_name = _get_os_name()

    if font_family != "auto":
        if font_exists(font_family):
            return ResolvedFont(name=font_family)
        logger.warning("지정된 폰트 '%s'를 찾을 수 없습니다. 폴백을 시도합니다.", font_family)

    chain = fallback_chain or KOREAN_FONT_CHAINS.get(os_name, [])
    for candidate in chain:
        if font_exists(candidate):
            is_fb = font_family != "auto"
            logger.info("폰트 선택: %s%s", candidate, " (폴백)" if is_fb else "")
            return ResolvedFont(name=candidate, is_fallback=is_fb)

    # 최종 폴백
    logger.warning("한글 폰트를 찾을 수 없습니다. '%s'로 폴백합니다.", UNIVERSAL_FALLBACK)
    return ResolvedFont(name=UNIVERSAL_FALLBACK, is_fallback=True)
