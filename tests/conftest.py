"""공통 테스트 fixture."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def tmp_output(tmp_path: Path) -> Path:
    """임시 출력 디렉토리."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture()
def sample_toml(tmp_path: Path) -> Path:
    """샘플 TOML 설정 파일."""
    toml_path = tmp_path / "topic.toml"
    toml_path.write_text(
        """\
topic = "AI 트렌드 2025-2026"
subtitle = "에이전틱 AI 시대"
theme = "dark"
output_dir = "./output"

[[sections]]
title = "개요"
content = "AI 기술의 급격한 발전"

[[sections]]
title = "LLM 경쟁 구도"
slide_type = "timeline"
""",
        encoding="utf-8",
    )
    return toml_path
