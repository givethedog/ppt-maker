"""palette.py 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest
from pptx.dml.color import RGBColor

from ppt_maker.errors import ConfigError
from ppt_maker.theme.palette import (
    DARK_PALETTE,
    DEFAULT_PALETTE,
    ColorPalette,
    FontConfig,
    ThemeConfig,
    hex_to_rgb,
)


class TestHexToRgb:
    def test_basic_conversion(self) -> None:
        assert hex_to_rgb("#1A1A2E") == RGBColor(0x1A, 0x1A, 0x2E)

    def test_without_hash(self) -> None:
        assert hex_to_rgb("00D2FF") == RGBColor(0x00, 0xD2, 0xFF)

    def test_white(self) -> None:
        assert hex_to_rgb("#FFFFFF") == RGBColor(0xFF, 0xFF, 0xFF)

    def test_black(self) -> None:
        assert hex_to_rgb("#000000") == RGBColor(0x00, 0x00, 0x00)

    def test_invalid_length_raises(self) -> None:
        with pytest.raises(ConfigError, match="잘못된 색상"):
            hex_to_rgb("#FFF")


class TestColorPalette:
    def test_from_dict(self) -> None:
        colors = {
            "bg_primary": "#1A1A2E",
            "bg_secondary": "#16213E",
            "accent": "#00D2FF",
            "accent2": "#7C3AED",
            "accent3": "#10B981",
            "text_primary": "#FFFFFF",
            "text_secondary": "#A0A0B0",
        }
        palette = ColorPalette.from_dict(colors)
        assert palette.bg_primary == RGBColor(0x1A, 0x1A, 0x2E)
        assert palette.accent == RGBColor(0x00, 0xD2, 0xFF)

    def test_missing_color_raises(self) -> None:
        with pytest.raises(ConfigError, match="필수 색상이 누락"):
            ColorPalette.from_dict({"bg_primary": "#000000"})

    def test_dark_palette_matches_create_slides(self) -> None:
        """현재 create_slides.py의 색상과 동일한 값 재현."""
        assert DARK_PALETTE.bg_primary == RGBColor(0x1A, 0x1A, 0x2E)
        assert DARK_PALETTE.accent == RGBColor(0x00, 0xD2, 0xFF)
        assert DARK_PALETTE.accent2 == RGBColor(0x7C, 0x3A, 0xED)
        assert DARK_PALETTE.accent3 == RGBColor(0x10, 0xB9, 0x81)

    def test_default_palette_is_light(self) -> None:
        assert DEFAULT_PALETTE.bg_primary == RGBColor(0xFA, 0xFA, 0xFC)
        assert DEFAULT_PALETTE.text_primary == RGBColor(0x1A, 0x1A, 0x2E)


class TestThemeConfig:
    def test_from_toml_dark(self) -> None:
        toml_path = Path(__file__).parent.parent / "src" / "ppt_maker" / "theme" / "themes" / "dark" / "theme.toml"
        theme = ThemeConfig.from_toml(toml_path)
        assert theme.name == "dark"
        assert theme.colors.bg_primary == RGBColor(0x1A, 0x1A, 0x2E)
        assert theme.fonts.heading == "Apple SD Gothic Neo"
        assert theme.slide.width == 13.333

    def test_from_toml_not_found(self) -> None:
        with pytest.raises(ConfigError, match="찾을 수 없습니다"):
            ThemeConfig.from_toml(Path("/nonexistent/theme.toml"))


class TestFontConfig:
    def test_from_dict(self) -> None:
        fc = FontConfig.from_dict({"heading": "Noto Sans KR", "body": "Noto Sans KR"})
        assert fc.heading == "Noto Sans KR"
        assert "Malgun Gothic" in fc.fallback

    def test_defaults(self) -> None:
        fc = FontConfig.from_dict({})
        assert fc.heading == "Apple SD Gothic Neo"
