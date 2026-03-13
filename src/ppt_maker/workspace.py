"""글로벌 워크스페이스 설정 — 템플릿 등록, 기본 설정 관리.

~/.config/ppt-maker/ 에 사용자 설정을 저장합니다.
"""

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from ppt_maker.errors import ConfigError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".config" / "ppt-maker"
CONFIG_FILE = CONFIG_DIR / "config.toml"
TEMPLATES_DIR = CONFIG_DIR / "templates"


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def load_global_config() -> dict:
    """글로벌 설정 로드. 없으면 빈 딕셔너리."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def save_global_config(config: dict) -> None:
    """글로벌 설정 저장."""
    import tomli_w

    _ensure_config_dir()
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config, f)
    logger.info("글로벌 설정 저장: %s", CONFIG_FILE)


def register_template(pptx_path: Path, name: str = "company") -> Path:
    """회사 템플릿을 등록 (복사 + 분석).

    Args:
        pptx_path: 원본 .pptx 파일 경로.
        name: 템플릿 이름 (기본: "company").

    Returns:
        등록된 템플릿 디렉토리 경로.
    """
    pptx_path = Path(pptx_path)
    if not pptx_path.exists():
        raise ConfigError(f"템플릿 파일을 찾을 수 없습니다: {pptx_path}")

    _ensure_config_dir()

    # 템플릿 디렉토리 생성
    template_dir = TEMPLATES_DIR / name
    template_dir.mkdir(parents=True, exist_ok=True)

    # 파일 복사
    dest = template_dir / "template.pptx"
    shutil.copy2(pptx_path, dest)
    logger.info("템플릿 복사: %s → %s", pptx_path, dest)

    # 분석 실행
    from ppt_maker.template.analyzer import analyze_template, save_manifest

    manifest = analyze_template(dest)
    manifest_path = template_dir / "manifest.toml"
    save_manifest(manifest, manifest_path)

    # 글로벌 설정 업데이트
    config = load_global_config()
    config["default_template"] = name
    config.setdefault("templates", {})[name] = {
        "path": str(dest),
        "manifest": str(manifest_path),
    }
    save_global_config(config)

    return template_dir


def get_registered_template(name: str | None = None) -> Path | None:
    """등록된 템플릿 .pptx 경로를 반환. 없으면 None."""
    config = load_global_config()
    name = name or config.get("default_template")
    if not name:
        return None

    templates = config.get("templates", {})
    entry = templates.get(name)
    if not entry:
        return None

    path = Path(entry["path"])
    return path if path.exists() else None


def get_template_manifest_path(name: str | None = None) -> Path | None:
    """등록된 템플릿의 매니페스트 경로를 반환."""
    config = load_global_config()
    name = name or config.get("default_template")
    if not name:
        return None

    templates = config.get("templates", {})
    entry = templates.get(name)
    if not entry:
        return None

    path = Path(entry.get("manifest", ""))
    return path if path.exists() else None


def is_template_registered() -> bool:
    """템플릿이 등록되어 있는지 확인."""
    return get_registered_template() is not None
