"""pandoc.py 단위 테스트."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from ppt_maker.converter.pandoc import check_pandoc, md_to_pptx
from ppt_maker.errors import PandocConversionError

# pandoc 설치 여부에 따라 스킵
has_pandoc = shutil.which("pandoc") is not None


@pytest.mark.skipif(not has_pandoc, reason="pandoc이 설치되어 있지 않음")
class TestPandoc:
    def test_check_pandoc(self) -> None:
        version = check_pandoc()
        assert "pandoc" in version.lower()

    def test_basic_conversion(self, tmp_path: Path) -> None:
        md = "# 테스트 제목\n\n## 섹션 1\n\n- 항목 1\n- 항목 2\n\n## 섹션 2\n\n내용"
        out = tmp_path / "test.pptx"
        result = md_to_pptx(md, out)
        assert result.exists()
        assert result.stat().st_size > 0

        # python-pptx로 열 수 있어야 함
        from pptx import Presentation
        prs = Presentation(str(result))
        assert len(prs.slides) >= 1

    def test_korean_content(self, tmp_path: Path) -> None:
        md = "# 한글 제목\n\n## 개요\n\n한글 내용 테스트입니다.\n\n- 항목 하나\n- 항목 둘"
        out = tmp_path / "korean.pptx"
        result = md_to_pptx(md, out)
        assert result.exists()

    def test_empty_markdown(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.pptx"
        result = md_to_pptx("", out)
        assert result.exists()
