"""theme manager 단위 테스트."""

from __future__ import annotations

import pytest

from ppt_maker.errors import ConfigError
from ppt_maker.theme.manager import ThemeManager


class TestThemeManager:
    def test_list_themes(self) -> None:
        tm = ThemeManager()
        themes = tm.list_themes()
        assert "dark" in themes
        assert "default" in themes

    def test_load_dark_theme(self) -> None:
        tm = ThemeManager()
        theme = tm.load_theme("dark")
        assert theme.name == "dark"

    def test_load_default_theme(self) -> None:
        tm = ThemeManager()
        theme = tm.load_theme("default")
        assert theme.name == "default"

    def test_load_nonexistent_theme(self) -> None:
        tm = ThemeManager()
        with pytest.raises(ConfigError, match="찾을 수 없습니다"):
            tm.load_theme("nonexistent_theme")

    def test_reference_pptx_returns_none_when_missing(self) -> None:
        tm = ThemeManager()
        assert tm.get_reference_pptx("dark") is None  # not yet created
