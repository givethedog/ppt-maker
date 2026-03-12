"""fonts 모듈 단위 테스트."""

from __future__ import annotations

import platform

import pytest

from ppt_maker.fonts.resolver import (
    KOREAN_FONT_CHAINS,
    ResolvedFont,
    font_exists,
    resolve_font,
)


class TestFontExists:
    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
    def test_apple_sd_gothic_neo_on_macos(self) -> None:
        assert font_exists("Apple SD Gothic Neo") is True

    def test_nonexistent_font(self) -> None:
        assert font_exists("ThisFontDoesNotExist12345") is False


class TestResolveFont:
    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
    def test_auto_on_macos(self) -> None:
        result = resolve_font("auto")
        assert isinstance(result, ResolvedFont)
        assert result.name in KOREAN_FONT_CHAINS["Darwin"]
        assert result.is_fallback is False

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
    def test_explicit_font(self) -> None:
        result = resolve_font("Apple SD Gothic Neo")
        assert result.name == "Apple SD Gothic Neo"
        assert result.is_fallback is False

    def test_missing_font_falls_back(self) -> None:
        result = resolve_font("ThisFontDoesNotExist12345")
        assert result.is_fallback is True

    def test_custom_fallback_chain(self) -> None:
        result = resolve_font("NoSuchFont", fallback_chain=["AlsoNoFont", "StillNo"])
        # Should end up at universal fallback
        assert result.is_fallback is True
