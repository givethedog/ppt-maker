"""테마 매니저 — 테마 로드, 전환, reference.pptx 경로 관리."""

from __future__ import annotations

import logging
from pathlib import Path

from ppt_maker.errors import ConfigError
from ppt_maker.theme.palette import ThemeConfig

logger = logging.getLogger(__name__)

BUILTIN_THEMES_DIR = Path(__file__).parent / "themes"


class ThemeManager:
    """테마 로더 및 관리자."""

    def __init__(self, themes_dir: Path | None = None) -> None:
        self._themes_dir = themes_dir or BUILTIN_THEMES_DIR

    def list_themes(self) -> list[str]:
        """사용 가능한 테마 이름 목록."""
        if not self._themes_dir.exists():
            return []
        return sorted(
            d.name
            for d in self._themes_dir.iterdir()
            if d.is_dir() and (d / "theme.toml").exists()
        )

    def load_theme(self, name: str) -> ThemeConfig:
        """이름으로 테마를 로드."""
        theme_dir = self._themes_dir / name
        toml_path = theme_dir / "theme.toml"
        if not toml_path.exists():
            available = self.list_themes()
            raise ConfigError(
                f"테마 '{name}'을(를) 찾을 수 없습니다.",
                detail=f"사용 가능한 테마: {', '.join(available) or '없음'}",
            )
        return ThemeConfig.from_toml(toml_path)

    def get_reference_pptx(self, name: str) -> Path | None:
        """테마의 reference.pptx 경로를 반환. 없으면 None."""
        ref_path = self._themes_dir / name / "reference.pptx"
        return ref_path if ref_path.exists() else None

    def get_theme_dir(self, name: str) -> Path:
        """테마 디렉토리 경로."""
        return self._themes_dir / name
