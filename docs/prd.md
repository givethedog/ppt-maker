# ppt-maker PRD (Product Requirements Document)

> **버전:** 1.0
> **작성일:** 2026-03-12
> **상태:** Draft -- 오픈 질문 해소 후 Approved로 전환

---

## 1. 프로젝트 개요

### 1-1. 비전

**"주제 하나만 입력하면, 조사부터 보고서, 프레젠테이션까지 자동으로."**

현재 `ppt-maker`는 AI 트렌드 발표 자료가 하드코딩된 단일 스크립트(`create_slides.py`)이다.
이를 **범용 보고서 + 프레젠테이션 자동 생성 파이프라인**으로 개편하여,
어떤 주제든 일관된 품질의 마크다운 보고서와 PPTX 슬라이드를 자동으로 만들어내는 도구로 발전시킨다.

### 1-2. 목표

| # | 목표 | 측정 기준 |
|---|------|----------|
| G1 | 주제 입력 → PPTX 출력까지 **단일 CLI 명령**으로 완료 | `ppt-maker generate --topic "주제"` 실행 후 .pptx 파일 생성 확인 |
| G2 | **Jinja2 템플릿** 기반으로 보고서 형식 일관성 확보 | 서로 다른 주제 2개로 생성한 보고서의 구조(목차, 섹션, 참고자료)가 동일 |
| G3 | **한글(Korean) 완벽 지원** -- 깨짐 없는 PPTX 출력 | Windows 10+, macOS에서 열어 한글 글자 깨짐(tofu) 0건 |
| G4 | 비개발자도 사용 가능한 **설치 및 실행 경험** | README의 설치 가이드만으로 IT팀 비개발자가 독립 실행 가능 |
| G5 | 기존 하드코딩 스크립트 대비 **재사용성** 확보 | 새 주제 추가 시 코드 수정 0줄 (설정/템플릿만 변경) |

### 1-3. 대상 사용자

| 페르소나 | 설명 | 핵심 니즈 |
|----------|------|----------|
| **IT팀 개발자** | Python 환경에 익숙, CLI 사용 가능 | 빠른 보고서 생성, 템플릿 커스터마이징 |
| **IT팀 비개발자** | 기본 터미널 사용 가능, Python 경험 제한적 | 간단한 명령어 하나로 결과물 획득, 명확한 설치 가이드 |
| **발표 준비 담당자** | 정기 발표 자료 작성 담당 | 일관된 디자인, 반복 작업 자동화 |

---

## 2. 핵심 기능 목록

### P0 -- Must Have (MVP)

| ID | 기능 | 설명 |
|----|------|------|
| F01 | **CLI 인터페이스** | `ppt-maker generate --topic "주제"` 명령으로 전체 파이프라인 실행. Click 또는 Typer 기반. |
| F02 | **콘텐츠 생성 (Content Generation)** | 입력된 주제에 대해 LLM을 활용하여 구조화된 마크다운 콘텐츠 생성. |
| F03 | **Jinja2 템플릿 렌더링** | 생성된 콘텐츠를 Jinja2 템플릿에 삽입하여 일관된 형식의 마크다운 보고서 출력. |
| F04 | **마크다운 → PPTX 변환** | pandoc으로 기본 구조 변환 후, python-pptx로 스타일링 및 한글 폰트 적용. |
| F05 | **한글 폰트 지원** | pptx-ea-font를 활용하여 PPTX 내 모든 텍스트에 한글 폰트(East Asian font) 적용. |
| F06 | **마크다운 보고서 저장** | 중간 산출물인 마크다운 보고서를 독립 파일로 저장 (`.md`). |

### P1 -- Should Have

| ID | 기능 | 설명 |
|----|------|------|
| F07 | **웹 검색 연동 (Web Research)** | 주제에 대한 실시간 자료 조사를 위해 웹 검색 API 연동 (Tavily, Perplexity 등). |
| F08 | **PPTX 테마 선택** | 복수의 PPTX 디자인 테마 중 선택 가능 (`--theme dark`, `--theme light`). |
| F09 | **슬라이드 수 제어** | `--slides 15` 옵션으로 목표 슬라이드 수 지정 (기본값: 20). |
| F10 | **설정 파일 (Config)** | `ppt-maker.yaml` 또는 `ppt-maker.toml`로 기본값 관리 (LLM 모델, 테마, 출력 경로 등). |
| F11 | **PDF 출력** | 마크다운 보고서를 PDF로도 출력 (`--format pdf`). |

### P2 -- Nice to Have

| ID | 기능 | 설명 |
|----|------|------|
| F12 | **차트/다이어그램 자동 생성** | Mermaid 또는 matplotlib 기반 시각화를 슬라이드에 삽입. |
| F13 | **멀티 언어 지원** | 영문, 한영 병기 보고서 생성 옵션. |
| F14 | **Git 워크플로우 자동화** | 보고서 생성 시 `report/{topic}-{date}` 브랜치 자동 생성 및 커밋. |
| F15 | **템플릿 갤러리** | 사용자 커뮤니티 또는 팀 내 템플릿 공유/검색. |
| F16 | **사용자 제공 자료 입력** | `--context file.md` 옵션으로 사용자가 직접 참고 자료를 제공. |

---

## 3. 사용자 스토리

### US-01: 기본 프레젠테이션 생성
**As a** IT팀 발표 담당자,
**I want** 주제만 입력하면 PPTX 슬라이드가 자동으로 생성되기를,
**So that** 반복적인 발표 자료 작성 시간을 절약할 수 있다.

**수용 기준 (Acceptance Criteria):**
- [ ] `ppt-maker generate --topic "클라우드 마이그레이션 전략"` 실행 시 `.pptx` 파일이 현재 디렉토리(또는 `--output` 경로)에 생성된다.
- [ ] 생성된 PPTX를 Microsoft PowerPoint 또는 LibreOffice Impress에서 정상적으로 열 수 있다.
- [ ] 명령 실행부터 파일 생성까지 **2분 이내**에 완료된다 (연구 단계 제외).
- [ ] 종료 코드(exit code)가 성공 시 0, 실패 시 non-zero이다.

### US-02: 한글 프레젠테이션 품질
**As a** 한국어 발표 자료를 만드는 사용자,
**I want** 생성된 PPTX의 한글이 깨지지 않고 올바른 폰트로 표시되기를,
**So that** 별도의 수동 폰트 수정 없이 바로 발표에 사용할 수 있다.

**수용 기준 (Acceptance Criteria):**
- [ ] PPTX 내 모든 텍스트 요소에 East Asian 폰트가 지정되어 있다 (`pptx-ea-font` 적용 확인).
- [ ] Windows 10+에서 열었을 때 한글 텍스트에 tofu(네모 깨짐)가 0건이다.
- [ ] macOS에서 열었을 때 한글 텍스트에 tofu가 0건이다.
- [ ] 특수 한글 조합(쌍자음, 겹받침 등)이 정상 렌더링된다.

### US-03: 마크다운 보고서 활용
**As a** 보고서 내용을 다른 용도로 재활용하고 싶은 사용자,
**I want** PPTX와 함께 마크다운 보고서 파일도 저장되기를,
**So that** 보고서 내용을 Notion, Confluence 등에 복사하거나 별도로 편집할 수 있다.

**수용 기준 (Acceptance Criteria):**
- [ ] PPTX 생성 시 동일 디렉토리에 `.md` 파일이 함께 생성된다.
- [ ] 마크다운 파일은 유효한 마크다운 문법을 따른다 (markdownlint 기준 critical error 0건).
- [ ] 마크다운 파일의 구조가 Jinja2 템플릿에 정의된 섹션(제목, 목차, 본문, 참고자료)을 모두 포함한다.

### US-04: 템플릿 기반 일관성
**As a** 정기적으로 발표 자료를 만드는 팀원,
**I want** 모든 보고서가 동일한 구조와 형식을 따르기를,
**So that** 팀 발표 자료의 품질과 형식이 일관되게 유지된다.

**수용 기준 (Acceptance Criteria):**
- [ ] 기본 제공 Jinja2 템플릿이 최소 1개 존재한다 (`templates/` 디렉토리).
- [ ] 서로 다른 주제 2개로 생성한 보고서의 구조적 섹션(제목, 목차, 섹션 구분, 참고자료)이 동일하다.
- [ ] 사용자가 `templates/` 디렉토리에 커스텀 템플릿을 추가하고 `--template custom.md.j2` 옵션으로 지정하면 해당 템플릿이 적용된다.

### US-05: 비개발자 설치 및 실행
**As a** Python에 익숙하지 않은 IT팀 비개발자,
**I want** 간단한 설치 가이드만으로 도구를 설치하고 실행할 수 있기를,
**So that** 개발자의 도움 없이 독립적으로 발표 자료를 생성할 수 있다.

**수용 기준 (Acceptance Criteria):**
- [ ] `pip install .` 또는 `pipx install .` 한 줄로 Python 패키지 설치가 완료된다.
- [ ] pandoc 미설치 상태에서 실행 시 `"pandoc이 설치되어 있지 않습니다. 설치 방법: ..."` 형태의 명확한 에러 메시지가 출력된다.
- [ ] `ppt-maker --help`가 모든 옵션을 한글 설명과 함께 표시한다.
- [ ] README에 macOS/Windows 각각의 설치 가이드가 포함된다.

### US-06: 콘텐츠 깊이 조절
**As a** 다양한 길이의 발표를 준비하는 사용자,
**I want** 슬라이드 수나 보고서 분량을 조절할 수 있기를,
**So that** 10분 짧은 브리핑부터 30분 심화 발표까지 대응할 수 있다.

**수용 기준 (Acceptance Criteria):**
- [ ] `--slides N` 옵션으로 목표 슬라이드 수를 지정할 수 있다 (기본값: 20).
- [ ] 생성된 슬라이드 수가 지정 값의 +/- 20% 이내이다.
- [ ] `--depth brief|standard|deep` 옵션으로 보고서 깊이를 선택할 수 있다.

### US-07: 설정 파일을 통한 기본값 관리
**As a** 반복적으로 도구를 사용하는 팀원,
**I want** 자주 쓰는 옵션(테마, 출력 경로, LLM 모델 등)을 설정 파일로 관리하기를,
**So that** 매번 긴 CLI 옵션을 입력하지 않아도 된다.

**수용 기준 (Acceptance Criteria):**
- [ ] 프로젝트 루트에 `ppt-maker.toml` (또는 `.yaml`) 파일이 있으면 자동으로 로드된다.
- [ ] CLI 옵션이 설정 파일 값을 override한다 (CLI > 설정 파일 > 기본값).
- [ ] `ppt-maker init` 명령으로 기본 설정 파일 템플릿을 생성할 수 있다.

### US-08: 기존 자료 마이그레이션
**As a** 기존 `presentation.md`를 이미 보유한 사용자,
**I want** 기존 마크다운 파일을 입력으로 사용하여 PPTX만 생성할 수 있기를,
**So that** 이미 작성된 보고서를 활용하여 슬라이드를 빠르게 만들 수 있다.

**수용 기준 (Acceptance Criteria):**
- [ ] `ppt-maker convert --input report.md` 명령으로 기존 마크다운 파일을 PPTX로 변환할 수 있다.
- [ ] LLM 호출 없이 마크다운 → PPTX 변환만 수행한다.
- [ ] 한글 폰트 적용 등 동일한 후처리가 적용된다.

---

## 4. 파이프라인 아키텍처 (Pipeline Architecture)

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────┐
│  Topic   │───→│  Research    │───→│  Jinja2       │───→│  pandoc      │───→│  .pptx   │
│  Input   │    │  (LLM/Web)  │    │  Template     │    │  + python-   │    │  Output  │
│  (CLI)   │    │             │    │  Rendering    │    │  pptx post-  │    │          │
└──────────┘    └──────────────┘    └───────┬───────┘    │  processing  │    └──────────┘
                                            │            └──────────────┘
                                            ↓
                                    ┌───────────────┐
                                    │  .md Report   │
                                    │  (saved)      │
                                    └───────────────┘
```

### 단계별 책임

| 단계 | 입력 | 출력 | 담당 모듈 |
|------|------|------|----------|
| 1. 주제 입력 | CLI argument | topic string | `cli.py` (Click/Typer) |
| 2. 자료 조사 | topic string | structured content (dict/JSON) | `researcher.py` |
| 3. 템플릿 렌더링 | content dict + Jinja2 template | markdown string | `renderer.py` |
| 4. 보고서 저장 | markdown string | `.md` file | `renderer.py` |
| 5. PPTX 변환 | `.md` file | raw `.pptx` | `converter.py` (pandoc wrapper) |
| 6. PPTX 후처리 | raw `.pptx` | styled `.pptx` with Korean fonts | `styler.py` (python-pptx + pptx-ea-font) |

---

## 5. 비기능 요구사항 (Non-Functional Requirements)

### 5-1. 성능 (Performance)

| 항목 | 기준 |
|------|------|
| 전체 파이프라인 실행 시간 | 주제 입력 → PPTX 출력: **120초 이내** (LLM 응답 시간 제외) |
| PPTX 후처리 시간 | python-pptx 스타일링 + 폰트 적용: **10초 이내** (30슬라이드 기준) |
| 메모리 사용량 | 피크 메모리 **500MB 이하** |
| 출력 파일 크기 | 텍스트 전용 PPTX: **10MB 이하** (이미지 포함 시 50MB 이하) |

### 5-2. 한글 지원 (Korean Language Support)

| 항목 | 기준 |
|------|------|
| 폰트 적용 범위 | 모든 텍스트 요소 (제목, 본문, 표, 목록) |
| 지원 폰트 | Malgun Gothic (Windows 기본), Apple SD Gothic Neo (macOS 기본), NanumGothic (크로스 플랫폼) |
| 특수 문자 | 한글 자모 조합, 쌍자음, 겹받침, 한자 병기 정상 렌더링 |
| 줄바꿈 | 한글 단어 단위 줄바꿈 (음절 단위 분리 방지) |

### 5-3. 호환성 (Compatibility)

| 항목 | 기준 |
|------|------|
| Python 버전 | 3.10 이상 |
| OS | macOS 12+, Windows 10+ |
| pandoc 버전 | 3.0 이상 |
| PPTX 호환 | Microsoft PowerPoint 2016+, LibreOffice Impress 7+, Google Slides (가져오기) |

### 5-4. 확장성 (Extensibility)

| 항목 | 기준 |
|------|------|
| 템플릿 추가 | `templates/` 디렉토리에 `.md.j2` 파일 추가만으로 새 보고서 형식 지원 |
| 테마 추가 | `themes/` 디렉토리에 `.pptx` 레퍼런스 파일 추가로 새 디자인 테마 지원 |
| LLM 프로바이더 | 환경변수 또는 설정 파일로 OpenAI / Anthropic / 로컬 모델 전환 가능 |
| 출력 형식 | 새로운 출력 형식(PDF, DOCX)을 converter 모듈 확장으로 추가 가능 |

### 5-5. 에러 처리 (Error Handling)

| 상황 | 기대 동작 |
|------|----------|
| pandoc 미설치 | 설치 안내를 포함한 명확한 에러 메시지 출력 후 exit code 1 |
| LLM API 키 미설정 | 어떤 환경변수가 필요한지 안내하는 에러 메시지 |
| LLM API 호출 실패 | 재시도 1회 후 실패 시 에러 메시지와 부분 결과(마크다운까지) 저장 |
| 잘못된 템플릿 | Jinja2 렌더링 에러를 사용자 친화적 메시지로 변환 |
| 출력 경로 권한 없음 | 명확한 권한 에러 메시지 |
| 네트워크 없음 (오프라인) | LLM 호출 불가 안내 + `--input` 옵션으로 기존 마크다운 사용 유도 |

---

## 6. 제약 조건 및 가정

### 6-1. 제약 조건 (Constraints)

| # | 제약 조건 | 영향 |
|---|----------|------|
| C1 | pandoc은 시스템 바이너리로 별도 설치 필요 | 설치 가이드에 OS별 pandoc 설치 방법 명시 필수 |
| C2 | LLM API 호출에 외부 네트워크 필요 | 오프라인 환경에서는 `convert` 명령(기존 MD → PPTX)만 사용 가능 |
| C3 | python-pptx는 기존 PPTX 수정만 가능 (디자인 도구 아님) | 시각적 품질은 pandoc 기본 레이아웃 + 후처리 수준으로 제한 |
| C4 | 대상 사용자 중 비개발자 포함 | CLI 옵션은 최소한으로, 에러 메시지는 한글로, 설치는 최대한 단순하게 |
| C5 | 기술 스택 확정 (Python, Jinja2, pandoc, python-pptx, Click/Typer) | 대안 기술 평가 불필요, 해당 스택 내에서 최적화 |

### 6-2. 가정 (Assumptions)

| # | 가정 | 검증 방법 |
|---|------|----------|
| A1 | 사용자 환경에 Python 3.10+가 설치되어 있다 | README에 Python 설치 가이드 포함, `python --version` 체크 로직 |
| A2 | pandoc이 한글 포함 마크다운을 PPTX로 정상 변환한다 | **MVP 착수 전 POC 필수** -- 한글 표, 목록, 제목 포함 테스트 마크다운으로 검증 |
| A3 | pptx-ea-font가 East Asian 폰트를 안정적으로 적용한다 | POC에서 Windows/macOS 양쪽 렌더링 확인 |
| A4 | LLM API (OpenAI 또는 Anthropic)에 접근 가능하다 | API 키 설정 가이드 제공, 키 미설정 시 명확한 안내 |
| A5 | `report/*` 브랜치 워크플로우는 수동 Git 운용이다 (P0에서는 도구가 Git을 조작하지 않음) | P2에서 자동화 검토 |
| A6 | 보고서당 LLM 토큰 비용은 허용 범위 내이다 | 생성 완료 후 사용 토큰 수 + 예상 비용 로깅 |

---

## 7. 프로젝트 구조 (Proposed)

```
ppt-maker/
├── pyproject.toml              # 패키지 설정, 의존성, CLI entry point
├── ppt-maker.toml              # 사용자 설정 파일 (기본값)
├── README.md                   # 설치 및 사용 가이드 (한글)
│
├── src/
│   └── ppt_maker/
│       ├── __init__.py
│       ├── cli.py              # CLI 인터페이스 (Click/Typer)
│       ├── researcher.py       # 자료 조사 모듈 (LLM 호출)
│       ├── renderer.py         # Jinja2 템플릿 렌더링
│       ├── converter.py        # pandoc 래퍼 (MD → PPTX)
│       ├── styler.py           # python-pptx 후처리 + 한글 폰트
│       ├── config.py           # 설정 로딩 (TOML/YAML)
│       └── models.py           # 데이터 모델 (Pydantic 등)
│
├── templates/
│   └── default.md.j2           # 기본 보고서 템플릿
│
├── themes/
│   └── default.pptx            # 기본 PPTX 레퍼런스 테마
│
├── tests/
│   ├── test_cli.py
│   ├── test_researcher.py
│   ├── test_renderer.py
│   ├── test_converter.py
│   └── test_styler.py
│
└── output/                     # 생성된 파일 (gitignored)
    ├── *.md
    └── *.pptx
```

---

## 8. 성공 지표 (Success Metrics)

### 8-1. 정량 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 파이프라인 성공률 | 주제 입력 → PPTX 출력 **95% 이상** 성공 | 10개 이상의 다양한 주제로 테스트 |
| 한글 렌더링 정확도 | 한글 깨짐 **0건** | Windows + macOS에서 PPTX 열어 시각 검수 |
| 설치 → 첫 실행 시간 | 비개발자 기준 **15분 이내** | 비개발자 팀원 1명에게 README만 제공하고 측정 |
| 보고서 생성 시간 | 주제 입력 → PPTX 파일 생성 완료 **2분 이내** | CLI 실행 시간 측정 (LLM 응답 시간 포함) |
| 코드 재사용성 | 새 주제 추가 시 코드 수정 **0줄** | 기존 코드를 수정하지 않고 새 주제로 실행 확인 |

### 8-2. 정성 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 보고서 품질 | 팀원 만족도 **4/5점 이상** | 생성된 보고서 3개를 팀원에게 리뷰 요청 |
| PPTX 디자인 | "수정 없이 발표 가능" 비율 **50% 이상** | 생성된 PPTX로 실제 발표 시도 후 수정 필요 항목 카운트 |
| CLI 사용성 | `--help`만으로 사용법 파악 가능 | 비개발자 팀원 피드백 |

---

## 9. 릴리스 계획 (Release Plan)

| 단계 | 범위 | 기간 (예상) | 마일스톤 |
|------|------|------------|----------|
| **POC** | pandoc 한글 PPTX 변환 검증 + pptx-ea-font 동작 확인 | 1-2일 | A2, A3 가정 검증 완료 |
| **MVP (v0.1)** | F01-F06 (CLI + LLM 콘텐츠 생성 + 템플릿 + PPTX 변환 + 한글 지원) | 1-2주 | 단일 명령으로 PPTX 생성 가능 |
| **v0.2** | F07-F10 (웹 검색, 테마, 슬라이드 수 제어, 설정 파일) | 1-2주 | 프로덕션 수준 사용 가능 |
| **v0.3** | F11-F16 (PDF, 차트, 다국어, Git 자동화) | 2-3주 | 풀 기능 |

---

## 10. 오픈 질문 (Open Questions)

> 아래 항목은 계획(planning) 단계 진입 전에 해소되어야 합니다.

- [ ] **자료 조사 데이터 소스** -- P0의 "자료 조사"는 LLM 자체 지식으로만 생성하는가, 아니면 웹 검색 API를 P0부터 포함하는가? 이 결정이 `researcher.py`의 의존성과 오프라인 동작 여부를 결정한다.
- [ ] **마크다운 보고서의 위상** -- 마크다운 파일은 최종 산출물(사용자에게 전달)인가, 아니면 중간 산출물(디버깅 용도)인가? 전자라면 별도의 품질 기준이 필요하다.
- [ ] **비개발자 실행 환경** -- 비개발자 사용자에게 Python + pandoc 직접 설치를 요구하는가, 아니면 Docker 이미지 등으로 패키징하는가?
- [ ] **PPTX 레퍼런스 테마** -- 팀에서 사용 중인 기존 PPTX 테마 파일(.pptx)이 있는가? 있다면 그것을 기반으로, 없다면 새로 디자인해야 한다.
- [ ] **LLM 프로바이더 우선순위** -- 기본 LLM은 OpenAI인가 Anthropic인가? 비용/품질 트레이드오프에 따라 기본값이 달라진다.
- [ ] **`report/*` 브랜치 자동화 범위** -- Git 브랜치 생성/커밋을 도구가 자동으로 수행해야 하는가, 아니면 사용자가 수동으로 관리하는가?

---

## 부록: 기존 코드 분석

### 현재 상태 (`create_slides.py`)

- **총 1,000+ 줄**의 하드코딩된 python-pptx 스크립트
- AI 트렌드 2025-2026 주제에 완전히 종속 (재사용 불가)
- 커스텀 다크 테마 (BG: `#1A1A2E`, Accent: `#00D2FF`)
- 한글 폰트: `Apple SD Gothic Neo` 직접 지정 (macOS 전용, Windows 미지원)
- 유틸리티 함수 (`set_bg`, `add_text`, `add_bullet_list`, `add_shape`)는 재사용 가능

### 마이그레이션 전략

1. 유틸리티 함수 → `styler.py`로 추출 및 일반화
2. 슬라이드 콘텐츠 → Jinja2 템플릿 데이터로 분리
3. 색상 팔레트 → 테마 설정 파일로 외부화
4. 폰트 → pptx-ea-font로 교체하여 크로스 플랫폼 지원
