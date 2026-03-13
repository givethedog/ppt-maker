"""errors.py 단위 테스트."""

from __future__ import annotations

from ppt_maker.errors import (
    ConfigError,
    ConfigFileNotFoundError,
    ConfigValidationError,
    FontError,
    PandocConversionError,
    PandocError,
    PandocNotFoundError,
    PipelineError,
    PptMakerError,
    PptxCustomError,
    TemplateError,
)


class TestErrorHierarchy:
    def test_all_inherit_from_base(self) -> None:
        errors = [
            ConfigError, TemplateError, PandocError,
            PptxCustomError, FontError, PipelineError,
        ]
        for err_cls in errors:
            assert issubclass(err_cls, PptMakerError)

    def test_pandoc_subclasses(self) -> None:
        assert issubclass(PandocNotFoundError, PandocError)
        assert issubclass(PandocConversionError, PandocError)

    def test_config_subclasses(self) -> None:
        assert issubclass(ConfigFileNotFoundError, ConfigError)
        assert issubclass(ConfigValidationError, ConfigError)


class TestErrorMessages:
    def test_pandoc_not_found_has_install_guide(self) -> None:
        err = PandocNotFoundError()
        assert "설치되어 있지 않습니다" in str(err)
        assert "brew install pandoc" in err.detail

    def test_config_file_not_found(self) -> None:
        err = ConfigFileNotFoundError("/some/path.toml")
        assert "/some/path.toml" in str(err)

    def test_config_validation_error(self) -> None:
        err = ConfigValidationError("topic", "비어 있음")
        assert "topic" in str(err)
        assert "비어 있음" in str(err)

    def test_pandoc_conversion_error(self) -> None:
        err = PandocConversionError("some stderr output")
        assert "변환 중 오류" in str(err)
        assert err.detail == "some stderr output"

    def test_base_error_detail(self) -> None:
        err = PptMakerError("테스트 에러", detail="상세 정보")
        assert str(err) == "테스트 에러"
        assert err.detail == "상세 정보"
