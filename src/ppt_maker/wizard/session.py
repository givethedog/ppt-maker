"""위저드 세션 상태 관리."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ppt_maker.config import SectionConfig


@dataclass
class WizardSession:
    """위저드 세션 상태."""

    session_id: str = ""
    output_dir: str = "./output"
    current_stage: str = "collect"  # collect → draft → research → review → generate → done

    # Stage 1: 수집 정보
    topic: str = ""
    subtitle: str = ""
    audience: str = "team"        # executive / team / general
    purpose: str = "report"       # report / proposal / training / review
    slide_count: int = 8
    tone: str = "professional"    # professional / technical / casual

    # 기존 설정
    theme: str = "default"
    font_family: str = "auto"
    llm_model: str = "gpt-4o-mini"
    llm_api_base: str = ""
    llm_api_key_env: str = "LLM_API_KEY"

    # 산출물 경로 (output_dir 기준 상대)
    draft_md: str = ""
    research_md: str = ""
    review_md: str = ""
    pptx_path: str = ""

    # 섹션 데이터
    sections: list[dict] = field(default_factory=list)

    # 타임스탬프
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.session_id:
            self.session_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def get_output_path(self) -> Path:
        return Path(self.output_dir)

    def get_sections(self) -> list[SectionConfig]:
        """sections dict 리스트를 SectionConfig 리스트로 변환."""
        result = []
        for s in self.sections:
            result.append(SectionConfig(
                title=s.get("title", ""),
                content=s.get("content", ""),
                slide_type=s.get("slide_type", "content"),
            ))
        return result

    def set_sections(self, configs: list[SectionConfig]) -> None:
        """SectionConfig 리스트를 dict 리스트로 저장."""
        self.sections = [
            {"title": s.title, "content": s.content, "slide_type": s.slide_type}
            for s in configs
        ]

    def advance_stage(self, next_stage: str) -> None:
        self.current_stage = next_stage
        self.updated_at = datetime.now(timezone.utc).isoformat()


STAGE_ORDER = ["collect", "draft", "research", "review", "generate", "done"]


def save_session(session: WizardSession) -> Path:
    """세션을 JSON 파일로 저장."""
    out = Path(session.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "session.json"
    data = asdict(session)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_session(path: Path) -> WizardSession:
    """JSON 파일에서 세션 로드."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return WizardSession(**data)
