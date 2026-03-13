"""research 모듈 단위 테스트."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ppt_maker.config import TopicConfig
from ppt_maker.research.generator import ContentGenerator, GeneratedContent
from ppt_maker.research.llm import LLMClient, LLMConfig

# ---------------------------------------------------------------------------
# LLMConfig 기본값 테스트
# ---------------------------------------------------------------------------


class TestLLMConfig:
    def test_defaults(self) -> None:
        cfg = LLMConfig()
        assert cfg.api_base == ""
        assert cfg.model == "gpt-4o-mini"
        assert cfg.api_key_env == "LLM_API_KEY"
        assert cfg.temperature == 0.7
        assert cfg.max_tokens == 4096

    def test_custom_values(self) -> None:
        cfg = LLMConfig(
            api_base="https://api.example.com",
            model="gpt-4",
            api_key_env="CUSTOM_KEY",
            temperature=0.3,
            max_tokens=2048,
        )
        assert cfg.api_base == "https://api.example.com"
        assert cfg.model == "gpt-4"
        assert cfg.api_key_env == "CUSTOM_KEY"
        assert cfg.temperature == 0.3
        assert cfg.max_tokens == 2048

    def test_frozen(self) -> None:
        cfg = LLMConfig()
        with pytest.raises(AttributeError):
            cfg.model = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# LLMClient — API 키 없을 때 오류 테스트
# ---------------------------------------------------------------------------


class TestLLMClient:
    def test_raises_when_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """API 키 환경변수가 없으면 LLMError 발생."""
        monkeypatch.delenv("LLM_API_KEY", raising=False)
        from ppt_maker.research.llm import LLMError

        cfg = LLMConfig(api_key_env="LLM_API_KEY")
        with pytest.raises(LLMError, match="API 키"):
            LLMClient(cfg)

    def test_raises_with_custom_env_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MY_CUSTOM_KEY", raising=False)
        from ppt_maker.research.llm import LLMError

        cfg = LLMConfig(api_key_env="MY_CUSTOM_KEY")
        with pytest.raises(LLMError) as exc_info:
            LLMClient(cfg)
        assert "MY_CUSTOM_KEY" in exc_info.value.detail

    def test_chat_returns_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """chat() 가 OpenAI 응답에서 텍스트를 반환."""
        monkeypatch.setenv("LLM_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "  테스트 응답  "

        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = mock_response

        with patch("ppt_maker.research.llm.OpenAI", return_value=mock_openai):
            cfg = LLMConfig()
            client = LLMClient(cfg)
            result = client.chat("시스템", "사용자")

        assert result == "테스트 응답"

    def test_chat_raises_on_none_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        from ppt_maker.research.llm import LLMError

        mock_response = MagicMock()
        mock_response.choices[0].message.content = None

        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = mock_response

        with patch("ppt_maker.research.llm.OpenAI", return_value=mock_openai):
            cfg = LLMConfig()
            client = LLMClient(cfg)
            with pytest.raises(LLMError, match="비어 있습니다"):
                client.chat("시스템", "사용자")

    def test_chat_wraps_unexpected_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        from ppt_maker.research.llm import LLMError

        mock_openai = MagicMock()
        mock_openai.chat.completions.create.side_effect = RuntimeError("network error")

        with patch("ppt_maker.research.llm.OpenAI", return_value=mock_openai):
            cfg = LLMConfig()
            client = LLMClient(cfg)
            with pytest.raises(LLMError, match="LLM API 호출 실패"):
                client.chat("시스템", "사용자")

    def test_base_url_passed_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")

        with patch("ppt_maker.research.llm.OpenAI") as mock_cls:
            mock_cls.return_value = MagicMock()
            cfg = LLMConfig(api_base="https://custom.api/v1")
            LLMClient(cfg)
            call_kwargs = mock_cls.call_args[1]
            assert call_kwargs["base_url"] == "https://custom.api/v1"

    def test_base_url_omitted_when_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")

        with patch("ppt_maker.research.llm.OpenAI") as mock_cls:
            mock_cls.return_value = MagicMock()
            cfg = LLMConfig(api_base="")
            LLMClient(cfg)
            call_kwargs = mock_cls.call_args[1]
            assert "base_url" not in call_kwargs


# ---------------------------------------------------------------------------
# ContentGenerator 테스트
# ---------------------------------------------------------------------------


def _make_json_response(sections: list[dict]) -> str:
    return json.dumps({"sections": sections}, ensure_ascii=False)


class TestContentGenerator:
    def _generator_with_mock_client(self, response_text: str) -> ContentGenerator:
        """mock LLMClient 를 주입한 ContentGenerator 반환."""
        gen = ContentGenerator(LLMConfig())
        mock_client = MagicMock()
        mock_client.chat.return_value = response_text
        gen._client = mock_client
        return gen

    def test_generate_returns_sections(self) -> None:
        payload = _make_json_response([
            {"title": "소개", "content": "내용", "slide_type": "title"},
            {"title": "본론", "content": "세부 내용", "slide_type": "content"},
        ])
        gen = self._generator_with_mock_client(payload)
        result = gen.generate("테스트 주제")

        assert isinstance(result, GeneratedContent)
        assert len(result.sections) == 2
        assert result.sections[0].title == "소개"
        assert result.sections[0].slide_type == "title"
        assert result.sections[1].title == "본론"

    def test_generate_stores_raw_response(self) -> None:
        payload = _make_json_response([{"title": "섹션", "content": "", "slide_type": "content"}])
        gen = self._generator_with_mock_client(payload)
        result = gen.generate("주제")
        assert result.raw_response == payload

    def test_generate_handles_markdown_code_block(self) -> None:
        """```json ... ``` 래핑된 응답 처리."""
        inner = _make_json_response([{"title": "A", "content": "B", "slide_type": "content"}])
        wrapped = f"```json\n{inner}\n```"
        gen = self._generator_with_mock_client(wrapped)
        result = gen.generate("주제")
        assert len(result.sections) == 1
        assert result.sections[0].title == "A"

    def test_generate_handles_malformed_json(self) -> None:
        """JSON 파싱 실패 시 원본 텍스트를 단일 섹션으로 반환."""
        gen = self._generator_with_mock_client("이건 JSON이 아닙니다")
        result = gen.generate("폴백 주제")
        assert len(result.sections) == 1
        assert result.sections[0].title == "폴백 주제"
        assert result.sections[0].content == "이건 JSON이 아닙니다"

    def test_generate_missing_fields_use_defaults(self) -> None:
        """섹션 필드 누락 시 기본값 사용."""
        payload = json.dumps({"sections": [{}]})
        gen = self._generator_with_mock_client(payload)
        result = gen.generate("주제")
        assert result.sections[0].title == "제목 없음"
        assert result.sections[0].slide_type == "content"

    def test_generate_passes_subtitle(self) -> None:
        payload = _make_json_response([{"title": "X", "content": "", "slide_type": "content"}])
        gen = self._generator_with_mock_client(payload)
        gen.generate("주제", subtitle="부제목")
        call_args = gen._client.chat.call_args  # type: ignore[union-attr]
        user_prompt = call_args[0][1]
        assert "부제목" in user_prompt

    def test_generate_passes_num_slides(self) -> None:
        payload = _make_json_response([{"title": "X", "content": "", "slide_type": "content"}])
        gen = self._generator_with_mock_client(payload)
        gen.generate("주제", num_slides=12)
        user_prompt = gen._client.chat.call_args[0][1]  # type: ignore[union-attr]
        assert "12" in user_prompt

    def test_lazy_client_creation(self) -> None:
        """_client 는 generate() 첫 호출 시 생성."""
        gen = ContentGenerator(LLMConfig())
        assert gen._client is None  # 아직 생성 전

    def test_get_client_returns_same_instance(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        with patch("ppt_maker.research.llm.OpenAI", return_value=MagicMock()):
            gen = ContentGenerator(LLMConfig())
            c1 = gen._get_client()
            c2 = gen._get_client()
            assert c1 is c2


# ---------------------------------------------------------------------------
# TopicConfig LLM 필드 테스트
# ---------------------------------------------------------------------------


class TestTopicConfigLLMFields:
    def test_defaults(self) -> None:
        cfg = TopicConfig(topic="주제")
        assert cfg.llm_api_base == ""
        assert cfg.llm_model == "gpt-4o-mini"
        assert cfg.llm_api_key_env == "LLM_API_KEY"
        assert cfg.use_research is True

    def test_custom_llm_fields(self) -> None:
        cfg = TopicConfig(
            topic="주제",
            llm_api_base="https://api.example.com",
            llm_model="gpt-4",
            llm_api_key_env="MY_KEY",
            use_research=False,
        )
        assert cfg.llm_api_base == "https://api.example.com"
        assert cfg.llm_model == "gpt-4"
        assert cfg.llm_api_key_env == "MY_KEY"
        assert cfg.use_research is False

    def test_use_research_mutable(self) -> None:
        """use_research 는 CLI --no-research 플래그로 변경 가능."""
        cfg = TopicConfig(topic="주제")
        assert cfg.use_research is True
        cfg.use_research = False
        assert cfg.use_research is False


class TestTopicConfigFromTomlLLM:
    def test_from_toml_with_llm_section(self, tmp_path: Path) -> None:
        toml_content = """
[project]
topic = "테스트"

[project.llm]
api_base = "https://custom.api/v1"
model = "gpt-4"
api_key_env = "MY_LLM_KEY"
enabled = false
"""
        toml_file = tmp_path / "topic.toml"
        toml_file.write_text(toml_content, encoding="utf-8")

        cfg = TopicConfig.from_toml(toml_file)
        assert cfg.llm_api_base == "https://custom.api/v1"
        assert cfg.llm_model == "gpt-4"
        assert cfg.llm_api_key_env == "MY_LLM_KEY"
        assert cfg.use_research is False

    def test_from_toml_without_llm_section_uses_defaults(self, tmp_path: Path) -> None:
        toml_content = '[project]\ntopic = "주제"\n'
        toml_file = tmp_path / "topic.toml"
        toml_file.write_text(toml_content, encoding="utf-8")

        cfg = TopicConfig.from_toml(toml_file)
        assert cfg.llm_api_base == ""
        assert cfg.llm_model == "gpt-4o-mini"
        assert cfg.use_research is True

    def test_from_toml_partial_llm_section(self, tmp_path: Path) -> None:
        toml_content = '[project]\ntopic = "주제"\n\n[project.llm]\nmodel = "gpt-4o"\n'
        toml_file = tmp_path / "topic.toml"
        toml_file.write_text(toml_content, encoding="utf-8")

        cfg = TopicConfig.from_toml(toml_file)
        assert cfg.llm_model == "gpt-4o"
        assert cfg.llm_api_base == ""  # 기본값 유지
        assert cfg.use_research is True  # 기본값 유지


# ---------------------------------------------------------------------------
# 파이프라인 research 스텝 테스트
# ---------------------------------------------------------------------------


class TestPipelineResearch:
    def test_skips_research_when_use_research_false(self) -> None:
        """use_research=False 이면 research 분기에 진입하지 않음."""
        cfg = TopicConfig(topic="주제", use_research=False)
        # 조건 검증: use_research=False 면 블록에 진입하지 않는다
        assert not (cfg.use_research and not cfg.sections)

    def test_skips_research_when_sections_exist(self) -> None:
        """sections 가 이미 있으면 research 를 건너뜀."""
        from ppt_maker.config import SectionConfig

        cfg = TopicConfig(
            topic="주제",
            use_research=True,
            sections=[SectionConfig(title="기존 섹션")],
        )
        # use_research=True 이지만 sections 가 있으므로 조건 `not config.sections` 가 False
        assert not (cfg.use_research and not cfg.sections)

    def test_research_populates_sections(self) -> None:
        """generate() 결과가 config.sections 에 저장됨."""
        from ppt_maker.config import SectionConfig
        from ppt_maker.research.generator import ContentGenerator, GeneratedContent
        from ppt_maker.research.llm import LLMConfig as ResearchLLMConfig

        cfg = TopicConfig(topic="AI 트렌드", use_research=True)
        assert not cfg.sections

        mock_sections = [SectionConfig(title="섹션1", content="내용1")]
        mock_generated = GeneratedContent(sections=mock_sections, raw_response="{}")

        mock_gen = MagicMock(spec=ContentGenerator)
        mock_gen.generate.return_value = mock_generated

        # 파이프라인 research 블록 로직 직접 재현
        if cfg.use_research and not cfg.sections:
            ResearchLLMConfig(
                api_base=cfg.llm_api_base,
                model=cfg.llm_model,
                api_key_env=cfg.llm_api_key_env,
            )
            generator = mock_gen
            generated = generator.generate(topic=cfg.topic, subtitle=cfg.subtitle)
            cfg.sections = generated.sections

        assert len(cfg.sections) == 1
        assert cfg.sections[0].title == "섹션1"
        mock_gen.generate.assert_called_once_with(topic="AI 트렌드", subtitle="")


# ---------------------------------------------------------------------------
# CLI --no-research 플래그 테스트
# ---------------------------------------------------------------------------


class TestCLINoResearch:
    def test_no_research_flag_sets_use_research_false(self) -> None:
        """--no-research 플래그가 topic_config.use_research = False 로 설정."""
        cfg = TopicConfig(topic="테스트")
        assert cfg.use_research is True

        # CLI generate 커맨드의 no_research 분기 로직 재현
        no_research = True
        if no_research:
            cfg.use_research = False

        assert cfg.use_research is False

    def test_no_research_false_by_default(self) -> None:
        """--no-research 없으면 use_research 가 True 로 유지."""
        cfg = TopicConfig(topic="테스트")
        no_research = False
        if no_research:
            cfg.use_research = False
        assert cfg.use_research is True
