"""ppt-maker 에러 계층 구조.

에러 처리 원칙:
- 설정/입력 오류: 즉시 실패 (fail fast)
- 변환 오류: 가능한 한 부분 성공 (graceful degradation)
- 모든 에러: 사용자가 이해할 수 있는 한국어 메시지 포함
"""

from __future__ import annotations


class PptMakerError(Exception):
    """ppt-maker 최상위 예외. 모든 프로젝트 예외의 기본 클래스."""

    def __init__(self, message: str, *, detail: str = "") -> None:
        self.detail = detail
        super().__init__(message)


# --- 설정 관련 ---


class ConfigError(PptMakerError):
    """설정 파일 파싱 또는 검증 실패.

    처리: 즉시 종료 + 명확한 메시지.
    """


class ConfigFileNotFoundError(ConfigError):
    """설정 파일을 찾을 수 없음."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"설정 파일을 찾을 수 없습니다: {path}",
            detail="파일 경로를 확인해 주세요.",
        )


class ConfigValidationError(ConfigError):
    """설정 값 검증 실패."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            f"설정 검증 실패 — {field}: {reason}",
            detail=f"'{field}' 필드의 값을 확인해 주세요.",
        )


# --- 템플릿 관련 ---


class TemplateError(PptMakerError):
    """Jinja2 렌더링 실패.

    처리: 즉시 종료 + 템플릿 위치/변수 정보.
    """


# --- pandoc 관련 ---


class PandocError(PptMakerError):
    """pandoc 관련 오류의 기본 클래스."""


class PandocNotFoundError(PandocError):
    """pandoc이 시스템에 설치되어 있지 않음.

    처리: 설치 안내 메시지 후 종료.
    """

    def __init__(self) -> None:
        super().__init__(
            "pandoc이 설치되어 있지 않습니다.",
            detail=(
                "설치 방법:\n"
                "  macOS:   brew install pandoc\n"
                "  Ubuntu:  sudo apt install pandoc\n"
                "  Windows: choco install pandoc"
            ),
        )


class PandocConversionError(PandocError):
    """pandoc 변환 중 오류 발생.

    처리: stderr 로깅 + 해당 섹션 건너뛰기 (graceful degradation).
    """

    def __init__(self, stderr: str) -> None:
        super().__init__(
            "pandoc 변환 중 오류가 발생했습니다.",
            detail=stderr,
        )


# --- python-pptx 관련 ---


class PptxCustomError(PptMakerError):
    """python-pptx 커스텀 슬라이드 생성 실패.

    처리: 해당 슬라이드 건너뛰기 + 경고 로깅.
    """


# --- 폰트 관련 ---


class FontError(PptMakerError):
    """폰트를 찾을 수 없음.

    처리: 폴백 폰트 사용 + 경고.
    """


# --- 파이프라인 관련 ---


class PipelineError(PptMakerError):
    """파이프라인 전체 실패.

    처리: 부분 결과물 저장 시도 + 에러 보고.
    """
