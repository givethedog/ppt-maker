"""pandoc 래퍼 — 마크다운 → PPTX 기본 변환."""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from ppt_maker.errors import PandocConversionError, PandocNotFoundError

logger = logging.getLogger(__name__)


def check_pandoc() -> str:
    """pandoc 설치 여부 및 버전 확인. 버전 문자열 반환."""
    pandoc_path = shutil.which("pandoc")
    if pandoc_path is None:
        raise PandocNotFoundError()
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        version_line = result.stdout.split("\n")[0]
        logger.info("pandoc 발견: %s", version_line)
        return version_line
    except (subprocess.TimeoutExpired, OSError) as e:
        raise PandocNotFoundError() from e


def md_to_pptx(
    markdown: str,
    output_path: Path,
    reference_doc: Path | None = None,
    slide_level: int = 2,
) -> Path:
    """마크다운을 pandoc으로 PPTX 변환.

    Args:
        markdown: 마크다운 문자열.
        output_path: 출력 PPTX 경로.
        reference_doc: reference.pptx 테마 파일 경로.
        slide_level: 슬라이드 분할 헤더 레벨 (기본 2 = ##).

    Returns:
        생성된 PPTX 파일 경로.
    """
    check_pandoc()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8",
    ) as f:
        f.write(markdown)
        md_path = Path(f.name)

    try:
        cmd = [
            "pandoc",
            str(md_path),
            "-t", "pptx",
            "-o", str(output_path),
            f"--slide-level={slide_level}",
        ]

        if reference_doc and reference_doc.exists():
            cmd.extend(["--reference-doc", str(reference_doc)])

        logger.info("pandoc 실행: %s", " ".join(cmd))

        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=120,
        )

        if result.returncode != 0:
            raise PandocConversionError(result.stderr)

        if result.stderr:
            logger.warning("pandoc 경고: %s", result.stderr.strip())

        logger.info("pandoc 변환 완료: %s", output_path)
        return output_path

    except subprocess.TimeoutExpired as e:
        raise PandocConversionError("pandoc 실행 시간 초과 (120초)") from e
    finally:
        md_path.unlink(missing_ok=True)
