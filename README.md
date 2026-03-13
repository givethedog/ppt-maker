# ppt-maker

주제 하나만 입력하면, LLM 조사부터 보고서, 프레젠테이션까지 자동으로 생성하는 파이프라인.

## 주요 기능

- **LLM 콘텐츠 자동 생성** — OpenAI 호환 API로 주제 기반 섹션 자동 구성
- **회사 템플릿 지원** — `.pptx` 템플릿 등록 후 레이아웃 자동 매핑 (BMW CI 20개 레이아웃 포함)
- **12종 슬라이드 타입** — title, section, content, comparison, timeline, quote, picture_left/right, blank, blank_dark, keynote, process
- **브랜드 이미지 자동 삽입** — 로컬 에셋 + Simple Icons CDN (30+ 브랜드)
- **하이브리드 변환** — pandoc (기본 슬라이드) + python-pptx (커스텀 슬라이드) 병합
- **한글 폰트 자동 탐색** — macOS/Linux/Windows 폰트 체인 + BMWGroupTN Condensed 우선

## 빠른 시작

```bash
# 초기 설정 (venv + .env + 의존성)
make setup

# .env 에서 LLM API 키 설정
vi .env

# 실행
make run TOPIC='AI 트렌드 2025-2026'
```

## 설치

```bash
# venv 생성 + 의존성 설치
make setup

# 또는 수동
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
```

### 필요 환경

- Python 3.10+
- pandoc (선택 — 없어도 커스텀 슬라이드로 동작)

## 사용법

### CLI 명령어

```bash
# LLM으로 콘텐츠 생성 + PPTX 변환
ppt-maker generate "클라우드 마이그레이션 전략"

# LLM 없이 (TOML 설정 파일 사용)
ppt-maker generate "주제" --config report.toml --no-research

# 마크다운만 미리보기
ppt-maker preview "주제"

# 환경 검증
ppt-maker check

# 회사 템플릿 등록 (최초 1회)
ppt-maker init --template BMW_CI_Template.pptx
```

### TOML 설정 파일

```toml
[project]
topic = "BMW IT 인프라 현황"
subtitle = "2025년 1분기 리포트"
author = "IT팀"
theme = "default"
output_dir = "./output"

[llm]
api_base = "https://your-api.example.com/v1"
model = "gpt-4o-mini"
api_key_env = "LLM_API_KEY"
enabled = true

[[sections]]
title = "현황 분석"
content = "- 서버 인프라 현황\n- 클라우드 전환율"
slide_type = "content"

[[sections]]
title = "비교"
slide_type = "comparison"
conversion_strategy = "custom"
```

### Make 명령어

```bash
make setup       # 전체 초기 설정
make dev         # 개발 의존성 설치
make test        # 테스트 실행
make lint        # ruff 린트
make run TOPIC='주제'         # 실행
make run-no-llm TOPIC='주제'  # LLM 없이 실행
make check       # 환경 검증
make clean       # 아티팩트 정리
```

## 환경변수 (.env)

```bash
LLM_API_KEY=your-api-key       # LLM API 키
LLM_API_BASE=https://...       # OpenAI 호환 API 엔드포인트
LLM_MODEL=gpt-4o-mini          # 모델 이름
```

## 프로젝트 구조

```
src/ppt_maker/
├── cli.py              # Typer CLI
├── config.py           # TopicConfig, SectionConfig
├── pipeline.py         # 파이프라인 오케스트레이터
├── research/
│   ├── llm.py          # OpenAI 호환 LLM 클라이언트
│   └── generator.py    # 주제 → 섹션 콘텐츠 생성
├── template/
│   ├── renderer.py     # Jinja2 마크다운 렌더러
│   └── analyzer.py     # .pptx 템플릿 분석기
├── converter/
│   ├── hybrid.py       # pandoc + python-pptx 하이브리드 엔진
│   ├── pandoc.py       # pandoc 래퍼
│   ├── pptx_custom.py  # 12종 커스텀 슬라이드 빌더
│   └── post_process.py # 폰트 후처리
├── assets/
│   ├── manager.py      # 에셋 매니저 (로컬 + CDN)
│   ├── simple_icons.py # Simple Icons CDN 클라이언트
│   └── converter.py    # SVG → PNG 변환
├── fonts/
│   └── resolver.py     # OS별 한글 폰트 탐색
├── theme/              # 테마 관리
├── workspace.py        # 회사 템플릿 등록/관리
└── errors.py           # 에러 계층
```

## 파이프라인 흐름

```
주제 입력
  → LLM 콘텐츠 생성 (research/)
  → Jinja2 마크다운 렌더링
  → pandoc 기본 슬라이드 변환
  → python-pptx 커스텀 슬라이드 빌드 + 병합
  → 폰트 후처리
  → report.md + report.pptx 출력
```

## 라이선스

MIT
