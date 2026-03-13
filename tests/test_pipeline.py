"""pipeline.py 통합 테스트."""

from __future__ import annotations

from pathlib import Path

from ppt_maker.config import SectionConfig, TopicConfig
from ppt_maker.pipeline import PipelineResult, run_pipeline


class TestPipeline:
    def test_basic_pipeline(self, tmp_path: Path) -> None:
        config = TopicConfig(
            topic="테스트 주제",
            subtitle="파이프라인 테스트",
            output_dir=tmp_path / "output",
            sections=[
                SectionConfig(title="개요", content="테스트 내용입니다."),
                SectionConfig(title="결론", content="마무리입니다."),
            ],
        )
        result = run_pipeline(config)
        assert isinstance(result, PipelineResult)
        assert result.markdown_path is not None
        assert result.markdown_path.exists()
        assert result.pptx_path is not None
        assert result.pptx_path.exists()
        assert result.slide_count >= 1
        assert result.elapsed_seconds > 0

    def test_markdown_content(self, tmp_path: Path) -> None:
        config = TopicConfig(
            topic="수입차 브랜드 IT 전략",
            output_dir=tmp_path / "output",
            sections=[SectionConfig(title="메르세데스-벤츠 DMS", content="DMS 통합 전략")],
        )
        result = run_pipeline(config)
        md_content = result.markdown_path.read_text(encoding="utf-8")
        assert "수입차 브랜드" in md_content
        assert "메르세데스-벤츠" in md_content

    def test_pptx_loadable(self, tmp_path: Path) -> None:
        from pptx import Presentation

        config = TopicConfig(
            topic="로드 테스트",
            output_dir=tmp_path / "output",
            sections=[SectionConfig(title="섹션 1", content="내용")],
        )
        result = run_pipeline(config)
        prs = Presentation(str(result.pptx_path))
        assert len(prs.slides) >= 1

    def test_empty_sections(self, tmp_path: Path) -> None:
        config = TopicConfig(
            topic="빈 섹션 테스트",
            output_dir=tmp_path / "output",
            use_research=False,
        )
        result = run_pipeline(config)
        assert result.markdown_path.exists()
        assert result.pptx_path.exists()
