# ppt-maker 기술 아키텍처 문서

> 버전: 1.0 | 작성일: 2026-03-12 | 상태: 초안

---

## 1. 프로젝트 개요

### 1.1 현재 상태

현재 `ppt-maker`는 단일 Python 스크립트(`create_slides.py`, 1,280줄)로 구성된 하드코딩 슬라이드 생성기이다.

```
현재 구조:
/Users/mung/git/ppt-maker/
├── create_slides.py       # 1,280줄 하드코딩 슬라이드 (python-pptx 직접 사용)
├── presentation.md        # 585줄 마크다운 보고서 (슬라이드와 연결 없음)
└── AI_트렌드_2025-2026.pptx  # 생성된 결과물
```

**핵심 문제점:**
- 콘텐츠와 프레젠테이션 로직이 완전히 결합되어 있음
- 새로운 주제에 대해 재사용 불가 (매번 전체 스크립트 재작성 필요)
- 마크다운 보고서와 슬라이드 간 연결 없음
- 폰트 처리가 `Apple SD Gothic Neo` 하드코딩 (크로스 플랫폼 미지원)
- 테스트, CLI, 패키지 구조 전무

### 1.2 목표 상태

**범용 보고서+프레젠테이션 자동 생성 파이프라인**으로 개편한다.

```
입력: 주제(topic) + 선택적 설정(config)
출력: 마크다운 보고서(.md) + PPTX 슬라이드(.pptx)
```

---

## 2. 전체 시스템 아키텍처

### 2.1 시스템 다이어그램 (ASCII)

```
                          ppt-maker 파이프라인
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐  │
  │  │  CLI    │───>│ Research │───>│ Template  │───>│ Converter │  │
  │  │(Typer)  │    │ Module   │    │ Renderer  │    │ Engine    │  │
  │  └─────────┘    └──────────┘    │ (Jinja2)  │    │           │  │
  │       │                         └───────────┘    │ ┌───────┐ │  │
  │       │  topic                       │           │ │pandoc │ │  │
  │       │  config                      │ .md       │ │(기본) │ │  │
  │       │  theme                       ▼           │ └───────┘ │  │
  │       │                         ┌───────────┐    │ ┌───────┐ │  │
  │       │                         │ Markdown  │───>│ │pptx   │ │  │
  │       │                         │ Report    │    │ │(커스텀)│ │  │
  │       │                         │ (.md)     │    │ └───────┘ │  │
  │       │                         └───────────┘    └─────┬─────┘  │
  │       │                                                │        │
  │       │         ┌───────────┐                          │        │
  │       └────────>│  Theme    │─────────────────────────>│        │
  │                 │  Manager  │  reference.pptx          │        │
  │                 └───────────┘                          ▼        │
  │                                                  ┌───────────┐  │
  │                                                  │   .pptx   │  │
  │                                                  │  Output   │  │
  │                                                  └───────────┘  │
  └──────────────────────────────────────────────────────────────────┘

  외부 의존성:
  ┌──────────┐  ┌──────────┐  ┌─────────────┐  ┌──────────────┐
  │ pandoc   │  │python-pptx│  │ pptx-ea-font│  │   Jinja2     │
  │ (시스템)  │  │  1.0.0   │  │ (한글 지원)  │  │ (템플릿)      │
  └──────────┘  └──────────┘  └─────────────┘  └──────────────┘
```

### 2.2 모듈 구조

```
ppt-maker/
├── pyproject.toml              # 패키지 관리, 의존성, CLI 엔트리포인트
├── README.md
├── src/
│   └── ppt_maker/
│       ├── __init__.py         # 패키지 초기화, 버전
│       ├── cli.py              # Typer CLI 인터페이스
│       ├── config.py           # 설정 스키마 (Pydantic/dataclass)
│       ├── pipeline.py         # 파이프라인 오케스트레이터
│       │
│       ├── research/           # 리서치 모듈 (향후 확장용)
│       │   ├── __init__.py
│       │   └── base.py         # 리서치 인터페이스 정의
│       │
│       ├── template/           # Jinja2 템플릿 시스템
│       │   ├── __init__.py
│       │   ├── renderer.py     # Jinja2 렌더러
│       │   ├── filters.py      # 커스텀 Jinja2 필터
│       │   └── templates/      # .md.j2 템플릿 파일들
│       │       ├── base.md.j2          # 기본 보고서 템플릿
│       │       ├── section.md.j2       # 섹션 블록
│       │       └── slide_hints.md.j2   # 슬라이드 힌트 주석
│       │
│       ├── converter/          # 변환 엔진
│       │   ├── __init__.py
│       │   ├── pandoc.py       # pandoc 래퍼 (MD -> PPTX 기본 변환)
│       │   ├── pptx_custom.py  # python-pptx 커스텀 슬라이드 생성
│       │   ├── hybrid.py       # pandoc + python-pptx 하이브리드 전략
│       │   └── post_process.py # PPTX 후처리 (폰트, 레이아웃 보정)
│       │
│       ├── theme/              # 테마 시스템
│       │   ├── __init__.py
│       │   ├── manager.py      # 테마 로더/관리
│       │   ├── palette.py      # 색상 팔레트 정의
│       │   └── themes/         # reference.pptx + 설정 파일
│       │       ├── default/
│       │       │   ├── reference.pptx
│       │       │   └── theme.toml
│       │       └── dark/
│       │           ├── reference.pptx
│       │           └── theme.toml
│       │
│       └── fonts/              # 폰트 처리
│           ├── __init__.py
│           ├── resolver.py     # OS별 폰트 탐색/폴백
│           └── korean.py       # 한글 폰트 특화 처리 (pptx-ea-font)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # 공통 fixture
│   ├── test_config.py
│   ├── test_renderer.py
│   ├── test_pandoc.py
│   ├── test_pptx_custom.py
│   ├── test_hybrid.py
│   ├── test_fonts.py
│   ├── test_pipeline.py
│   └── test_cli.py
│
└── examples/                   # 예제
    ├── ai_trends/
    │   ├── topic.toml          # 주제 설정 예제
    │   └── presentation.md     # 기존 마크다운 (마이그레이션 참조)
    └── simple/
        └── topic.toml
```

---

## 3. 데이터 흐름

### 3.1 전체 파이프라인 흐름

```
[1] CLI 입력
    │
    │  TopicConfig {
    │    topic: str
    │    sections: list[SectionConfig]
    │    theme: str = "default"
    │    output_dir: Path
    │    font_family: str = "auto"
    │  }
    │
    ▼
[2] Research (선택적, 향후 확장)
    │
    │  ResearchResult {
    │    topic: str
    │    sections: list[SectionData]
    │    metadata: dict
    │  }
    │
    ▼
[3] Template Rendering (Jinja2)
    │
    │  입력: ResearchResult + TopicConfig
    │  처리: .md.j2 템플릿에 데이터 바인딩
    │  출력: rendered_report.md (순수 마크다운)
    │
    │  RenderedReport {
    │    markdown: str
    │    slide_hints: list[SlideHint]  # <!-- slide: type=table --> 같은 힌트
    │    metadata: ReportMetadata
    │  }
    │
    ▼
[4] Conversion Strategy 결정
    │
    │  ConversionPlan {
    │    sections: list[{
    │      content: str
    │      strategy: "pandoc" | "custom"  # 섹션별 전략
    │      slide_type: str                # title, content, table, diagram, ...
    │    }]
    │  }
    │
    ▼
[5-A] pandoc 변환 (기본 슬라이드)          [5-B] python-pptx 변환 (커스텀 슬라이드)
    │  - 텍스트 중심 콘텐츠                    │  - 타임라인, 비교표, 인포그래픽
    │  - 불릿 리스트                          │  - 커스텀 레이아웃
    │  - 기본 표                              │  - 복잡한 다이어그램
    │  - reference.pptx 테마 적용             │  - 데이터 시각화
    │                                         │
    ▼                                         ▼
[6] PPTX 병합 + 후처리
    │
    │  - pandoc 결과와 커스텀 슬라이드 병합
    │  - 한글 폰트 일괄 적용 (pptx-ea-font)
    │  - 슬라이드 번호 재부여
    │  - 레이아웃 정합성 검증
    │
    ▼
[7] 최종 출력
    │
    ├── report.md     (마크다운 보고서)
    └── report.pptx   (프레젠테이션)
```

### 3.2 단계별 입출력 스키마 (Python 타입 기준)

```python
# --- [1] CLI 입력 ---
@dataclass
class TopicConfig:
    topic: str                          # "AI 트렌드 2025-2026"
    subtitle: str = ""                  # "에이전틱 AI 시대와 n8n의 가능성"
    author: str = ""
    date: str = ""                      # 자동 생성 가능
    sections: list[SectionConfig] = []  # 비어있으면 자동 구성
    theme: str = "default"              # themes/ 하위 디렉토리명
    output_dir: Path = Path("./output")
    font_family: str = "auto"           # auto, apple-sd, noto-sans-kr
    slide_width: float = 13.333         # inches (16:9)
    slide_height: float = 7.5

@dataclass
class SectionConfig:
    title: str
    content: str = ""                   # 직접 제공 또는 리서치로 채움
    slide_type: str = "auto"            # auto, title, content, table, timeline, ...
    conversion_strategy: str = "auto"   # auto, pandoc, custom

# --- [3] 렌더링 결과 ---
@dataclass
class RenderedReport:
    markdown: str                       # 완성된 마크다운 문자열
    slide_hints: list[SlideHint]        # 마크다운 내 슬라이드 힌트
    metadata: dict                      # title, date, section_count 등

@dataclass
class SlideHint:
    section_index: int
    slide_type: str                     # title, content, table, timeline, ...
    conversion_strategy: str            # pandoc, custom
    extra: dict = field(default_factory=dict)

# --- [4] 변환 계획 ---
@dataclass
class ConversionPlan:
    pandoc_sections: list[str]          # pandoc으로 변환할 마크다운 조각
    custom_sections: list[CustomSlideSpec]  # python-pptx로 만들 슬라이드 명세
    theme_path: Path                    # reference.pptx 경로
    merge_order: list[tuple[str, int]]  # ("pandoc", 0), ("custom", 0), ...

@dataclass
class CustomSlideSpec:
    slide_type: str
    data: dict                          # 슬라이드 타입별 구조화 데이터
    layout_hint: str = ""
```

---

## 4. 핵심 설계 결정

### 4.1 pandoc vs python-pptx: 하이브리드 전략

**원칙: pandoc을 기본으로, python-pptx는 pandoc이 못 하는 것만 담당한다.**

| 슬라이드 유형 | 변환 엔진 | 이유 |
|-------------|----------|------|
| 타이틀 슬라이드 | pandoc | YAML 메타데이터로 충분 |
| 텍스트 + 불릿 | pandoc | 마크다운 기본 요소 |
| 기본 표 (단순) | pandoc | pipe table 지원 |
| 코드 블록 | pandoc | 기본 지원 |
| 인용문 | pandoc | blockquote 지원 |
| 복잡한 표 (색상, 병합) | python-pptx | pandoc 표는 스타일링 제한 |
| 타임라인/프로세스 | python-pptx | 커스텀 도형 배치 필요 |
| 비교 카드 (좌우 분할) | python-pptx | 2-column 레이아웃 필요 |
| 인포그래픽 | python-pptx | 도형, 색상, 위치 제어 필요 |
| 데이터 차트 | python-pptx | 막대/원형 차트 API |
| 스펙트럼/포지션 맵 | python-pptx | 커스텀 도형 배치 |

**결정 로직:**

```
마크다운 섹션 분석
├── slide_hint 주석이 있으면 → 힌트 따름
├── 표가 있고 3열 이하, 색상 불필요 → pandoc
├── 표가 있고 4열 이상 또는 색상/병합 필요 → python-pptx
├── ASCII 다이어그램 포함 → python-pptx (도형 변환)
├── 불릿/텍스트만 → pandoc
└── 기본값 → pandoc
```

### 4.2 pandoc reference.pptx 테마 시스템

pandoc은 `--reference-doc=reference.pptx` 옵션으로 테마를 적용한다.

**reference.pptx 구성 요구사항:**

```
reference.pptx 내 필수 슬라이드 레이아웃:
├── Title Slide           # pandoc의 title metadata에 사용
├── Section Header        # ## 헤더에 사용
├── Two Content           # 2-column 레이아웃
├── Title and Content     # 기본 콘텐츠 슬라이드
├── Blank                 # 커스텀 슬라이드 삽입 기반
└── Comparison            # 비교 슬라이드
```

**테마 설정 파일 (`theme.toml`):**

```toml
[meta]
name = "dark"
description = "어두운 배경 테마 (현재 create_slides.py 스타일)"

[colors]
bg_primary = "#1A1A2E"
bg_secondary = "#16213E"
accent = "#00D2FF"
accent2 = "#7C3AED"
accent3 = "#10B981"
text_primary = "#FFFFFF"
text_secondary = "#A0A0B0"

[fonts]
heading = "Apple SD Gothic Neo"
body = "Apple SD Gothic Neo"
fallback = ["Noto Sans KR", "Malgun Gothic", "sans-serif"]

[slide]
width = 13.333    # inches
height = 7.5      # inches
```

### 4.3 한글 폰트 전략

```
폰트 해결 순서:
1. 설정 파일에 명시된 font_family 확인
2. font_family == "auto" 이면:
   ├── macOS → Apple SD Gothic Neo
   ├── Linux → Noto Sans KR (fc-list로 확인)
   └── Windows → Malgun Gothic
3. 선택된 폰트 시스템 존재 여부 검증 (fc-list / 레지스트리)
4. 없으면 폴백 체인 탐색
5. pptx-ea-font로 PPTX 내 EA(East Asian) 폰트 속성 일괄 적용
```

**pptx-ea-font 적용 시점:** 최종 PPTX 생성 후 후처리 단계에서 일괄 적용한다. pandoc 생성 슬라이드와 python-pptx 커스텀 슬라이드 모두에 균일하게 적용하기 위함이다.

### 4.4 에러 처리 전략

```
에러 계층:
├── ConfigError          # 설정 파일 파싱/검증 실패
│   └── 처리: 즉시 종료 + 명확한 메시지
├── TemplateError        # Jinja2 렌더링 실패
│   └── 처리: 즉시 종료 + 템플릿 위치/변수 정보
├── PandocError          # pandoc 실행 실패
│   ├── PandocNotFoundError   # pandoc 미설치
│   │   └── 처리: 설치 안내 메시지 후 종료
│   └── PandocConversionError # 변환 중 오류
│       └── 처리: stderr 로깅 + 해당 섹션 건너뛰기 (graceful degradation)
├── PptxCustomError      # python-pptx 커스텀 슬라이드 생성 실패
│   └── 처리: 해당 슬라이드 건너뛰기 + 경고 로깅
├── FontError            # 폰트 미발견
│   └── 처리: 폴백 폰트 사용 + 경고
└── PipelineError        # 파이프라인 전체 실패
    └── 처리: 부분 결과물 저장 시도 + 에러 보고
```

**원칙:**
- 설정/입력 오류: 즉시 실패 (fail fast)
- 변환 오류: 가능한 한 부분 성공 (graceful degradation)
- 모든 에러: 사용자가 이해할 수 있는 한국어 메시지 포함

---

## 5. 의존성 관계

### 5.1 외부 의존성

```toml
# pyproject.toml [project.dependencies]
[project]
dependencies = [
    "python-pptx>=1.0.0",
    "pptx-ea-font>=0.1.0",
    "Jinja2>=3.1",
    "typer>=0.9",
    "rich>=13.0",         # CLI 출력 포맷팅
    "tomli>=2.0;python_version<'3.11'",  # TOML 파싱 (3.11 미만)
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
]
```

**시스템 의존성:**
- `pandoc` >= 3.0 (시스템 설치 필요, `brew install pandoc` / `apt install pandoc`)
- Python >= 3.10

### 5.2 내부 모듈 의존성

```
cli.py
  └─> pipeline.py
        ├─> config.py
        ├─> research/base.py        (향후)
        ├─> template/renderer.py
        │     └─> template/filters.py
        ├─> converter/hybrid.py
        │     ├─> converter/pandoc.py
        │     │     └─> (외부: pandoc CLI)
        │     └─> converter/pptx_custom.py
        │           └─> theme/palette.py
        ├─> converter/post_process.py
        │     └─> fonts/korean.py
        │           └─> fonts/resolver.py
        └─> theme/manager.py
              └─> theme/palette.py
```

---

## 6. 커스텀 슬라이드 타입 카탈로그

현재 `create_slides.py`에서 사용되는 패턴을 분석하여 재사용 가능한 슬라이드 타입으로 추출한다.

| 타입 ID | 설명 | 현재 코드 사용 예 | 필수 데이터 |
|---------|------|-----------------|-----------|
| `title` | 타이틀 슬라이드 | 슬라이드 1 (line 80) | title, subtitle, date |
| `quote` | 인용/질문 슬라이드 | 슬라이드 2 (line 101) | quote, attribution |
| `glossary` | 용어 설명 그리드 | 슬라이드 3 (line 114) | terms: [{name, abbr, desc}] |
| `timeline` | 타임라인 | 슬라이드 4 (line 163) | events: [{date, title, color}] |
| `card_list` | 카드형 목록 | 슬라이드 5 (line 207) | items: [{title, detail, note}] |
| `comparison` | 좌우 비교 | 슬라이드 7 (line 279) | left: {title, items}, right: {title, items} |
| `process` | 단계별 프로세스 | 슬라이드 11 (line 617) | steps: [{label, desc}] |
| `grid_cards` | 2x3 또는 3x2 그리드 | 슬라이드 12 (line 657) | cards: [{title, desc, detail}] |
| `progress_bars` | 진행률 바 차트 | 슬라이드 13 (line 696) | bars: [{label, value, max}] |
| `spectrum` | 스펙트럼/포지션 맵 | 슬라이드 18 (line 942) | axis_label, points: [{name, position}] |
| `bridge` | 브릿지/전환 슬라이드 | 슬라이드 10 (line 552) | items, conclusion |
| `key_value_grid` | 키-값 그리드 | 슬라이드 16 (line 860) | pairs: [{key, value}] |

---

## 7. 백엔드 개발 태스크 목록

### 7.1 프로젝트 인프라

#### BE-001: pyproject.toml 및 프로젝트 구조 초기화

- **설명:** `pyproject.toml` 생성, `src/ppt_maker/` 패키지 구조 설정, 의존성 정의, CLI 엔트리포인트 등록. `ruff` 린터 설정 포함.
- **의존성:** 없음 (최초 태스크)
- **예상 복잡도:** S
- **수용 기준:**
  - `pip install -e .` 로 개발 모드 설치 성공
  - `ppt-maker --help` 명령이 동작
  - `ruff check src/` 통과
  - Python 3.10+ 호환 확인

#### BE-002: 설정 스키마 정의 (config.py)

- **설명:** `TopicConfig`, `SectionConfig`, `SlideHint` 등 핵심 데이터 클래스 정의. TOML 파일 로딩 지원. 입력 검증 로직 포함.
- **의존성:** BE-001
- **예상 복잡도:** S
- **수용 기준:**
  - `TopicConfig` 가 TOML 파일로부터 로드 가능
  - 필수 필드 누락 시 명확한 `ConfigError` 발생
  - 기본값이 올바르게 적용됨
  - 단위 테스트 3개 이상

#### BE-003: 에러 처리 체계 구축

- **설명:** 프로젝트 전용 예외 클래스 계층 구조 정의 (`ConfigError`, `TemplateError`, `PandocError`, `PptxCustomError`, `FontError`, `PipelineError`). 한국어 에러 메시지 포함.
- **의존성:** BE-001
- **예상 복잡도:** S
- **수용 기준:**
  - 모든 예외 클래스가 정의되고 적절한 계층 구조를 가짐
  - 각 예외에 사용자 친화적 한국어 메시지 포함
  - CLI에서 에러 발생 시 트레이스백 대신 깨끗한 메시지 출력

---

### 7.2 테마 시스템

#### BE-004: 색상 팔레트 모듈 (palette.py)

- **설명:** 현재 `create_slides.py` 라인 10-20의 하드코딩된 색상을 `theme.toml` 기반 색상 팔레트 시스템으로 추출. `RGBColor` 래퍼 포함.
- **의존성:** BE-002
- **예상 복잡도:** S
- **수용 기준:**
  - `theme.toml` 에서 색상 로드 가능
  - hex 문자열 (`#1A1A2E`) -> `RGBColor` 자동 변환
  - 기본 테마 (`default`, `dark`) 2개 포함
  - 현재 `create_slides.py`의 색상과 동일한 값 재현

#### BE-005: reference.pptx 테마 생성 및 테마 매니저

- **설명:** pandoc용 `reference.pptx` 파일 생성 도구 구현. 필수 슬라이드 레이아웃 포함. `ThemeManager` 클래스로 테마 로드/전환 관리.
- **의존성:** BE-004
- **예상 복잡도:** M
- **수용 기준:**
  - `reference.pptx` 에 6개 필수 레이아웃 포함 (Title, Section Header, Two Content, Title and Content, Blank, Comparison)
  - 테마 이름으로 `reference.pptx` 경로 조회 가능
  - `theme.toml`에서 폰트, 색상, 슬라이드 크기 로드 가능
  - `dark` 테마가 현재 `create_slides.py`의 스타일 재현

---

### 7.3 템플릿 시스템

#### BE-006: Jinja2 렌더러 기본 구현

- **설명:** Jinja2 환경 설정, 템플릿 로더, 기본 렌더링 파이프라인 구현. `RenderedReport` 출력.
- **의존성:** BE-002
- **예상 복잡도:** M
- **수용 기준:**
  - `.md.j2` 템플릿 파일을 렌더링하여 `.md` 생성
  - `TopicConfig` 데이터를 템플릿에 바인딩 가능
  - 존재하지 않는 변수 참조 시 `TemplateError` 발생
  - 한글 콘텐츠 정상 렌더링

#### BE-007: 커스텀 Jinja2 필터 구현

- **설명:** 마크다운 생성에 유용한 커스텀 필터: `md_table` (딕셔너리 -> 마크다운 표), `md_bullet` (리스트 -> 불릿), `slide_hint` (슬라이드 변환 힌트 주석 삽입).
- **의존성:** BE-006
- **예상 복잡도:** S
- **수용 기준:**
  - `{{ data | md_table }}` 로 마크다운 표 생성
  - `{{ items | md_bullet }}` 로 불릿 리스트 생성
  - `{{ "timeline" | slide_hint }}` 로 `<!-- slide: type=timeline -->` 생성
  - 한글 표 컬럼 정렬 정상 동작

#### BE-008: 기본 보고서 템플릿 작성

- **설명:** 범용 보고서용 `base.md.j2` 템플릿 작성. 현재 `presentation.md`의 구조를 참조하되, 데이터 기반으로 유연하게 렌더링 가능하도록 설계.
- **의존성:** BE-006, BE-007
- **예상 복잡도:** M
- **수용 기준:**
  - 임의의 `TopicConfig` 로 보고서 생성 가능
  - 현재 `presentation.md` 와 유사한 구조/품질의 출력
  - 섹션 수가 가변적 (3~15개)
  - 슬라이드 힌트 주석이 적절히 삽입됨

---

### 7.4 변환 파이프라인

#### BE-009: pandoc 래퍼 구현

- **설명:** pandoc CLI 호출 래퍼. 마크다운 -> PPTX 변환, `--reference-doc` 옵션 적용, stderr 캡처 및 에러 처리.
- **의존성:** BE-003, BE-005
- **예상 복잡도:** M
- **수용 기준:**
  - 마크다운 문자열 입력 -> PPTX 파일 출력
  - `reference.pptx` 테마 적용 확인
  - pandoc 미설치 시 `PandocNotFoundError` + 설치 안내
  - pandoc 변환 실패 시 `PandocConversionError` + stderr 내용
  - 한글 마크다운 변환 정상 동작

#### BE-010: python-pptx 커스텀 슬라이드 빌더

- **설명:** 섹션 6의 슬라이드 타입 카탈로그 기반으로, 구조화된 데이터에서 커스텀 슬라이드를 생성하는 빌더 패턴 구현. 현재 `create_slides.py`의 `set_bg`, `add_shape`, `add_text`, `add_bullet_list` 헬퍼(라인 30-74)를 리팩토링하여 재사용.
- **의존성:** BE-004
- **예상 복잡도:** L
- **수용 기준:**
  - 최소 6개 슬라이드 타입 지원: `title`, `quote`, `timeline`, `comparison`, `card_list`, `process`
  - 각 타입이 딕셔너리 데이터 입력으로 슬라이드 생성
  - 테마 팔레트 색상 자동 적용
  - 현재 `create_slides.py`와 시각적으로 유사한 품질의 출력

#### BE-011: 슬라이드 힌트 파서

- **설명:** 마크다운 내 `<!-- slide: type=timeline, strategy=custom -->` 형태의 힌트 주석을 파싱하여 `ConversionPlan` 생성. 힌트 없는 섹션의 자동 전략 결정 로직 포함.
- **의존성:** BE-002
- **예상 복잡도:** M
- **수용 기준:**
  - HTML 주석 형태 힌트 파싱 정상 동작
  - 힌트 없는 섹션에 대해 콘텐츠 분석 기반 자동 전략 결정
  - `ConversionPlan` 객체 생성 및 검증
  - 에지 케이스: 빈 섹션, 힌트만 있는 섹션 등

#### BE-012: 하이브리드 변환 엔진

- **설명:** `ConversionPlan`에 따라 pandoc 변환과 python-pptx 커스텀 변환을 조합하여 최종 PPTX를 생성하는 하이브리드 엔진. 슬라이드 병합 및 순서 관리.
- **의존성:** BE-009, BE-010, BE-011
- **예상 복잡도:** L
- **수용 기준:**
  - pandoc 슬라이드와 커스텀 슬라이드가 하나의 PPTX로 병합
  - 슬라이드 순서가 원본 마크다운 순서와 일치
  - 테마(배경색, 폰트)가 양쪽 슬라이드에 일관 적용
  - 부분 실패 시 성공한 슬라이드만으로 결과물 생성 (graceful degradation)

---

### 7.5 한글/폰트 처리

#### BE-013: OS별 폰트 탐색기 (resolver.py)

- **설명:** macOS/Linux/Windows에서 시스템 폰트 목록 조회 및 특정 폰트 존재 여부 확인. 한글 폰트 폴백 체인 구현.
- **의존성:** BE-001
- **예상 복잡도:** M
- **수용 기준:**
  - macOS에서 `Apple SD Gothic Neo` 탐지
  - Linux에서 `Noto Sans KR` 탐지 (`fc-list` 활용)
  - 지정 폰트 미존재 시 폴백 체인 자동 적용
  - `font_family="auto"` 시 OS별 최적 한글 폰트 자동 선택

#### BE-014: pptx-ea-font 한글 폰트 후처리

- **설명:** 최종 PPTX에 대해 `pptx-ea-font`를 사용하여 EA(East Asian) 폰트 속성을 일괄 적용. pandoc 생성 슬라이드와 python-pptx 커스텀 슬라이드 모두에 적용.
- **의존성:** BE-013
- **예상 복잡도:** S
- **수용 기준:**
  - 모든 텍스트 요소에 EA 폰트 적용 확인
  - pandoc으로 생성된 슬라이드의 한글이 정상 렌더링
  - python-pptx로 생성된 슬라이드의 한글이 정상 렌더링
  - Windows/macOS/Linux에서 PPTX 열었을 때 한글 깨짐 없음

#### BE-015: PPTX 후처리 파이프라인 (post_process.py)

- **설명:** 폰트 적용 외 추가 후처리: 슬라이드 번호 삽입, 빈 슬라이드 제거, 레이아웃 정합성 검증.
- **의존성:** BE-012, BE-014
- **예상 복잡도:** M
- **수용 기준:**
  - 슬라이드 번호가 footer에 자동 삽입
  - 내용 없는 슬라이드 자동 제거
  - 후처리 전/후 슬라이드 수 로깅

---

### 7.6 파이프라인 오케스트레이션

#### BE-016: 파이프라인 오케스트레이터 (pipeline.py)

- **설명:** 전체 파이프라인을 순차 실행: config 로드 -> 템플릿 렌더링 -> 변환 전략 결정 -> 변환 실행 -> 후처리 -> 출력. 각 단계 로깅, 진행률 표시.
- **의존성:** BE-006, BE-012, BE-015
- **예상 복잡도:** M
- **수용 기준:**
  - `TopicConfig` 입력으로 `.md` + `.pptx` 생성
  - 각 단계 시작/완료 로깅
  - 중간 단계 실패 시 에러 보고 + 가능한 부분 결과 저장
  - 전체 실행 시간 측정 및 보고

---

### 7.7 CLI 인터페이스

#### BE-017: Typer CLI 기본 구현

- **설명:** `ppt-maker generate` 커맨드 구현. 주요 옵션: `--topic`, `--config` (TOML 파일), `--theme`, `--output-dir`, `--font`. `rich` 기반 진행률 표시.
- **의존성:** BE-016
- **예상 복잡도:** M
- **수용 기준:**
  - `ppt-maker generate --topic "주제" --output-dir ./out` 실행 가능
  - `ppt-maker generate --config topic.toml` 파일 기반 실행 가능
  - `--help` 에 한국어 설명 포함
  - 진행률 바 또는 스피너 표시
  - 에러 시 종료 코드 1 + 명확한 메시지

#### BE-018: CLI 부가 커맨드

- **설명:** `ppt-maker themes` (사용 가능 테마 목록), `ppt-maker check` (pandoc/폰트 등 환경 검증), `ppt-maker preview` (마크다운만 생성, PPTX 변환 건너뜀).
- **의존성:** BE-017
- **예상 복잡도:** S
- **수용 기준:**
  - `ppt-maker themes` 에서 설치된 테마 목록 출력
  - `ppt-maker check` 에서 pandoc 버전, 한글 폰트 존재 여부 확인
  - `ppt-maker preview --topic "주제"` 로 `.md` 만 생성

---

### 7.8 테스트

#### BE-019: 단위 테스트 (config, template, fonts)

- **설명:** `config.py`, `template/renderer.py`, `template/filters.py`, `fonts/resolver.py`에 대한 단위 테스트.
- **의존성:** BE-002, BE-006, BE-007, BE-013
- **예상 복잡도:** M
- **수용 기준:**
  - 각 모듈 커버리지 80% 이상
  - 에지 케이스 (빈 입력, 잘못된 TOML, 폰트 미존재) 테스트
  - `pytest` 로 전체 통과
  - CI 실행 가능한 수준 (외부 의존성 mock)

#### BE-020: 통합 테스트 (pandoc, converter)

- **설명:** pandoc 래퍼, 커스텀 슬라이드 빌더, 하이브리드 엔진의 통합 테스트. 실제 PPTX 파일 생성 및 검증.
- **의존성:** BE-009, BE-010, BE-012
- **예상 복잡도:** M
- **수용 기준:**
  - 마크다운 입력 -> PPTX 파일 생성 end-to-end 테스트
  - 생성된 PPTX의 슬라이드 수 검증
  - 한글 텍스트 포함 슬라이드 정상 생성 확인
  - pandoc 미설치 환경에서 graceful skip (`pytest.mark.skipif`)

#### BE-021: E2E 테스트 (파이프라인 + CLI)

- **설명:** CLI 커맨드 실행부터 최종 출력 파일 생성까지 E2E 테스트. 현재 `presentation.md`의 주제를 사용한 회귀 테스트 포함.
- **의존성:** BE-016, BE-017
- **예상 복잡도:** M
- **수용 기준:**
  - `ppt-maker generate --config examples/ai_trends/topic.toml` E2E 실행 성공
  - `.md` 파일과 `.pptx` 파일 모두 생성 확인
  - 생성된 `.pptx` 파일이 손상되지 않음 (`python-pptx`로 로드 가능)
  - 한글 콘텐츠 정상 포함 확인

#### BE-022: 기존 create_slides.py 마이그레이션 검증

- **설명:** 현재 `create_slides.py`로 생성한 PPTX와 새 파이프라인으로 생성한 PPTX를 비교하여 시각적 품질이 동등한지 검증하는 테스트.
- **의존성:** BE-021
- **예상 복잡도:** S
- **수용 기준:**
  - 새 파이프라인 출력 슬라이드 수 >= 기존 30장
  - 주요 슬라이드 타입(타이틀, 타임라인, 비교, 그리드) 시각적 검증
  - 색상 팔레트 일치 확인
  - 한글 렌더링 동등성 확인

---

## 8. 태스크 의존성 그래프

```
BE-001 (프로젝트 구조)
  ├─> BE-002 (설정 스키마)
  │     ├─> BE-004 (팔레트) ──> BE-005 (테마 매니저)
  │     ├─> BE-006 (Jinja2 렌더러) ──> BE-007 (필터) ──> BE-008 (템플릿)
  │     └─> BE-011 (힌트 파서)
  ├─> BE-003 (에러 처리) ──> BE-009 (pandoc 래퍼)
  └─> BE-013 (폰트 탐색) ──> BE-014 (한글 후처리)

BE-010 (커스텀 슬라이드) <── BE-004

BE-012 (하이브리드 엔진) <── BE-009, BE-010, BE-011

BE-015 (후처리) <── BE-012, BE-014

BE-016 (파이프라인) <── BE-006, BE-012, BE-015

BE-017 (CLI 기본) <── BE-016
  └─> BE-018 (CLI 부가)

BE-019 (단위 테스트) <── BE-002, BE-006, BE-007, BE-013
BE-020 (통합 테스트) <── BE-009, BE-010, BE-012
BE-021 (E2E 테스트) <── BE-016, BE-017
BE-022 (마이그레이션 검증) <── BE-021
```

## 9. 구현 우선순위 (권장 순서)

| 단계 | 태스크 | 설명 |
|------|--------|------|
| **Phase 1: 기반** | BE-001, BE-002, BE-003 | 프로젝트 구조, 설정, 에러 처리 |
| **Phase 2: 테마+폰트** | BE-004, BE-005, BE-013, BE-014 | 테마/폰트 시스템 (PPTX 품질의 기초) |
| **Phase 3: 템플릿** | BE-006, BE-007, BE-008 | Jinja2 기반 마크다운 생성 |
| **Phase 4: 변환** | BE-009, BE-010, BE-011, BE-012, BE-015 | pandoc + python-pptx 하이브리드 변환 |
| **Phase 5: 통합** | BE-016, BE-017, BE-018 | 파이프라인 + CLI |
| **Phase 6: 검증** | BE-019, BE-020, BE-021, BE-022 | 테스트 + 마이그레이션 검증 |

---

## 10. 주요 기술적 리스크

| 리스크 | 영향 | 완화 전략 |
|--------|------|----------|
| pandoc PPTX 출력 품질이 기대 이하 | 높음 | python-pptx 커스텀 비중 확대 (하이브리드 전략의 유연성) |
| pandoc + python-pptx 슬라이드 병합 시 테마 불일치 | 중간 | 후처리 단계에서 일괄 스타일 적용, reference.pptx 정교하게 설계 |
| pptx-ea-font가 pandoc 출력에 대해 EA 폰트를 완전히 적용하지 못할 가능성 | 중간 | 직접 XML 조작 폴백 구현 (python-pptx의 lxml 접근) |
| 한글 표 정렬 문제 (고정폭/가변폭 혼합) | 낮음 | Jinja2 필터에서 유니코드 너비 계산 (unicodedata.east_asian_width) |
| 마크다운 -> 슬라이드 분할 기준 모호성 | 중간 | 슬라이드 힌트 주석 시스템으로 명시적 제어, 자동 분할은 `---` 또는 `##` 기준 |
