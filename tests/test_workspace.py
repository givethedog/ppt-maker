"""workspace 모듈 테스트."""

from __future__ import annotations

import pytest

from ppt_maker.workspace import (
    _ensure_config_dir,
    get_registered_template,
    get_template_manifest_path,
    is_template_registered,
    load_global_config,
    save_global_config,
)


@pytest.fixture()
def tmp_config_dir(tmp_path, monkeypatch):
    """임시 설정 디렉토리로 교체."""
    config_dir = tmp_path / ".config" / "ppt-maker"
    templates_dir = config_dir / "templates"
    config_file = config_dir / "config.toml"

    monkeypatch.setattr("ppt_maker.workspace.CONFIG_DIR", config_dir)
    monkeypatch.setattr("ppt_maker.workspace.CONFIG_FILE", config_file)
    monkeypatch.setattr("ppt_maker.workspace.TEMPLATES_DIR", templates_dir)

    return config_dir


def test_ensure_config_dir_creates_dirs(tmp_config_dir):
    _ensure_config_dir()
    assert tmp_config_dir.exists()
    assert (tmp_config_dir / "templates").exists()


def test_load_global_config_empty(tmp_config_dir):
    result = load_global_config()
    assert result == {}


def test_save_and_load_global_config(tmp_config_dir):
    config = {"default_template": "company", "some_key": "value"}
    save_global_config(config)
    loaded = load_global_config()
    assert loaded["default_template"] == "company"
    assert loaded["some_key"] == "value"


def test_get_registered_template_none(tmp_config_dir):
    assert get_registered_template() is None


def test_get_registered_template_exists(tmp_config_dir):
    # 템플릿 파일 생성
    tpl_dir = tmp_config_dir / "templates" / "company"
    tpl_dir.mkdir(parents=True)
    tpl_file = tpl_dir / "template.pptx"
    tpl_file.write_bytes(b"fake pptx")

    config = {
        "default_template": "company",
        "templates": {
            "company": {
                "path": str(tpl_file),
                "manifest": str(tpl_dir / "manifest.toml"),
            }
        },
    }
    save_global_config(config)

    result = get_registered_template()
    assert result == tpl_file


def test_get_registered_template_missing_file(tmp_config_dir):
    config = {
        "default_template": "company",
        "templates": {
            "company": {
                "path": "/nonexistent/template.pptx",
                "manifest": "/nonexistent/manifest.toml",
            }
        },
    }
    save_global_config(config)
    assert get_registered_template() is None


def test_get_template_manifest_path(tmp_config_dir):
    tpl_dir = tmp_config_dir / "templates" / "test"
    tpl_dir.mkdir(parents=True)
    manifest = tpl_dir / "manifest.toml"
    manifest.write_text("[template]")

    config = {
        "default_template": "test",
        "templates": {
            "test": {
                "path": str(tpl_dir / "template.pptx"),
                "manifest": str(manifest),
            }
        },
    }
    save_global_config(config)

    result = get_template_manifest_path()
    assert result == manifest


def test_is_template_registered_false(tmp_config_dir):
    assert not is_template_registered()


def test_is_template_registered_true(tmp_config_dir):
    tpl_dir = tmp_config_dir / "templates" / "company"
    tpl_dir.mkdir(parents=True)
    tpl_file = tpl_dir / "template.pptx"
    tpl_file.write_bytes(b"fake")

    config = {
        "default_template": "company",
        "templates": {"company": {"path": str(tpl_file), "manifest": ""}},
    }
    save_global_config(config)
    assert is_template_registered()
