"""색상 팔레트 모듈.

theme.toml 기반 색상 팔레트 시스템. hex 문자열 → RGBColor 자동 변환.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from pptx.dml.color import RGBColor

from ppt_maker.errors import ConfigError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def hex_to_rgb(hex_color: str) -> RGBColor:
    """'#1A1A2E' 형태의 hex 문자열을 RGBColor로 변환."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ConfigError(f"잘못된 색상 코드: #{hex_color}", detail="6자리 hex 코드를 사용하세요.")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return RGBColor(r, g, b)


@dataclass(frozen=True)
class ColorPalette:
    """테마 색상 팔레트."""

    bg_primary: RGBColor
    bg_secondary: RGBColor
    accent: RGBColor
    accent2: RGBColor
    accent3: RGBColor
    text_primary: RGBColor
    text_secondary: RGBColor

    @classmethod
    def from_dict(cls, colors: dict[str, str]) -> ColorPalette:
        """딕셔너리(hex 문자열)에서 팔레트를 생성."""
        required = ["bg_primary", "bg_secondary", "accent", "accent2", "accent3",
                     "text_primary", "text_secondary"]
        missing = [k for k in required if k not in colors]
        if missing:
            raise ConfigError(
                f"팔레트에 필수 색상이 누락되었습니다: {', '.join(missing)}",
            )
        return cls(**{k: hex_to_rgb(colors[k]) for k in required})


@dataclass(frozen=True)
class FontConfig:
    """테마 폰트 설정."""

    heading: str = "Apple SD Gothic Neo"
    body: str = "Apple SD Gothic Neo"
    fallback: tuple[str, ...] = ("Noto Sans KR", "Malgun Gothic", "sans-serif")

    @classmethod
    def from_dict(cls, fonts: dict) -> FontConfig:
        fallback = fonts.get("fallback", ["Noto Sans KR", "Malgun Gothic", "sans-serif"])
        return cls(
            heading=fonts.get("heading", "Apple SD Gothic Neo"),
            body=fonts.get("body", "Apple SD Gothic Neo"),
            fallback=tuple(fallback),
        )


@dataclass(frozen=True)
class SlideSize:
    """슬라이드 크기 (인치)."""

    width: float = 13.333
    height: float = 7.5


@dataclass(frozen=True)
class ThemeConfig:
    """theme.toml에서 로드한 전체 테마 설정."""

    name: str
    description: str
    colors: ColorPalette
    fonts: FontConfig
    slide: SlideSize = field(default_factory=SlideSize)

    @classmethod
    def from_toml(cls, path: Path) -> ThemeConfig:
        """theme.toml 파일에서 테마를 로드."""
        if not path.exists():
            raise ConfigError(f"테마 파일을 찾을 수 없습니다: {path}")
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            raise ConfigError(f"테마 파일 파싱 실패: {path}", detail=str(e)) from e

        meta = data.get("meta", {})
        return cls(
            name=meta.get("name", path.parent.name),
            description=meta.get("description", ""),
            colors=ColorPalette.from_dict(data.get("colors", {})),
            fonts=FontConfig.from_dict(data.get("fonts", {})),
            slide=SlideSize(
                width=data.get("slide", {}).get("width", 13.333),
                height=data.get("slide", {}).get("height", 7.5),
            ),
        )


# --- 기본 테마 팔레트 (하드코딩 폴백) ---

DARK_PALETTE = ColorPalette(
    bg_primary=RGBColor(0x1A, 0x1A, 0x2E),
    bg_secondary=RGBColor(0x16, 0x21, 0x3E),
    accent=RGBColor(0x00, 0xD2, 0xFF),
    accent2=RGBColor(0x7C, 0x3A, 0xED),
    accent3=RGBColor(0x10, 0xB9, 0x81),
    text_primary=RGBColor(0xFF, 0xFF, 0xFF),
    text_secondary=RGBColor(0xA0, 0xA0, 0xB0),
)

DEFAULT_PALETTE = ColorPalette(
    bg_primary=RGBColor(0xFA, 0xFA, 0xFC),
    bg_secondary=RGBColor(0xF0, 0xF0, 0xF5),
    accent=RGBColor(0x00, 0x66, 0xFF),
    accent2=RGBColor(0x7C, 0x3A, 0xED),
    accent3=RGBColor(0x10, 0xB9, 0x81),
    text_primary=RGBColor(0x1A, 0x1A, 0x2E),
    text_secondary=RGBColor(0x6B, 0x70, 0x80),
)
