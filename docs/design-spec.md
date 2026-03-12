# ppt-maker 디자인 요구사항 문서

**작성일:** 2026-03-12
**버전:** 1.0
**대상:** 수입차 브랜드 IT팀 (비개발자 포함)
**파이프라인:** 주제 입력 → 마크다운 보고서 + PPTX 슬라이드 자동 생성

---

## 목차

1. [현재 디자인 현황 분석](#1-현재-디자인-현황-분석)
2. [디자인 시스템 요구사항](#2-디자인-시스템-요구사항)
   - 2.1 PPTX 테마 설계
   - 2.2 색상 팔레트 시스템
   - 2.3 타이포그래피
   - 2.4 시각적 요소
3. [마크다운 보고서 템플릿 디자인](#3-마크다운-보고서-템플릿-디자인)
4. [프론트/테마 개발 태스크 목록](#4-프론트테마-개발-태스크-목록)

---

## 1. 현재 디자인 현황 분석

### 현재 구현 (`create_slides.py` 기준)

| 항목 | 현재값 | 비고 |
|------|--------|------|
| 슬라이드 크기 | 13.333" × 7.5" | 와이드스크린 16:9, 유지 |
| 배경 색상 | `#1A1A2E` (진한 남색) | BG_DARK |
| 서브 배경 | `#16213E` (중간 남색) | BG_MID |
| 강조색 1 | `#00D2FF` (시안) | ACCENT |
| 강조색 2 | `#7C3AED` (보라) | ACCENT2 |
| 강조색 3 | `#10B981` (에메랄드) | ACCENT3 |
| 경고색 | `#FF6B35` (오렌지) | ORANGE |
| 주목색 | `#FFD600` (옐로) | YELLOW |
| 브랜드색 | `#EA4B71` (핑크) | N8N_COLOR |
| 폰트 | Apple SD Gothic Neo | macOS 전용, 이식성 문제 |
| 슬라이드 생성 방식 | python-pptx 직접 코딩 | 레이아웃 하드코딩 |

### 현재 구현의 문제점

1. **폰트 의존성:** Apple SD Gothic Neo는 macOS/iOS 전용. Windows 환경에서 렌더링 깨짐.
2. **테마 단일화:** 다크 테마만 지원. 비즈니스/프레젠테이션 용도에 따라 라이트 테마 수요 발생 가능.
3. **레이아웃 하드코딩:** 슬라이드별 좌표값이 Python 코드에 직접 명시되어 재사용·유지보수 어려움.
4. **reference.pptx 없음:** pandoc 파이프라인 미연결. 현재는 python-pptx 단독 생성.
5. **색상 시스템 미분리:** 색상이 파일 상단에 전역 상수로 선언되어 있으나, 테마 교체 인터페이스 없음.
6. **컴포넌트 추상화 부족:** `add_text`, `add_shape` 등 저수준 헬퍼만 있고, 슬라이드 단위 컴포넌트 없음.

---

## 2. 디자인 시스템 요구사항

### 2.1 PPTX 테마 설계

#### 슬라이드 크기 (유지)

```
Width:  13.333 inches (9,144,000 EMU)
Height: 7.5 inches   (6,858,000 EMU)
Ratio:  16:9 와이드스크린
```

#### 필수 슬라이드 레이아웃 6종

pandoc의 `reference.pptx`와 python-pptx 직접 생성 양쪽 모두에서 사용.

---

**레이아웃 1: Title Slide (타이틀 슬라이드)**

용도: 발표 첫 장, 섹션 전환 강조 슬라이드

```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│   [CENTERED TITLE]                          │
│   좌: 1.0"  상: 2.2"  폭: 11.3"  높: 1.5"  │
│   폰트: 48pt, Bold, White                   │
│                                             │
│   [CENTERED SUBTITLE]                       │
│   좌: 1.0"  상: 3.9"  폭: 11.3"  높: 0.8"  │
│   폰트: 24pt, Regular, Accent               │
│                                             │
│   [DATE/META]                               │
│   좌: 1.0"  상: 5.0"  폭: 11.3"  높: 0.5"  │
│   폰트: 14pt, Regular, LightGray            │
│                                             │
│   [ACCENT LINE]                             │
│   좌: 3.0"  상: 5.7"  폭: 7.3"   높: 0.04" │
│   색상: Accent1                             │
└─────────────────────────────────────────────┘
```

플레이스홀더:
- `idx=0`: Title (Center Title)
- `idx=1`: Subtitle
- `idx=13`: Date (optional)

---

**레이아웃 2: Section Header (섹션 구분)**

용도: 각 챕터 시작, 내용 전환점

```
┌─────────────────────────────────────────────┐
│ [LEFT ACCENT BAR]                           │
│ 좌: 0"    상: 0"    폭: 0.25"  높: 7.5"    │
│ 색상: Accent1                               │
│                                             │
│          [SECTION NUMBER]                  │
│          좌: 1.2"  상: 2.5"  폰트: 14pt    │
│          색상: Accent1, Uppercase           │
│                                             │
│          [SECTION TITLE]                   │
│          좌: 1.2"  상: 3.0"  폭: 10"       │
│          폰트: 40pt, Bold, White            │
│                                             │
│          [SECTION DESCRIPTION]             │
│          좌: 1.2"  상: 4.2"  폭: 9"        │
│          폰트: 18pt, Regular, LightGray     │
└─────────────────────────────────────────────┘
```

플레이스홀더:
- `idx=0`: Title
- `idx=1`: Body (Description)

---

**레이아웃 3: Title and Content (제목 + 콘텐츠)**

용도: 일반 콘텐츠 슬라이드 (텍스트, 테이블, 차트)

```
┌─────────────────────────────────────────────┐
│ [TOP RULE]                                  │
│ 좌: 0.5"  상: 0.9"  폭: 12.3"  높: 0.04"  │
│ 색상: Accent1                               │
│                                             │
│ [TITLE]                                     │
│ 좌: 0.5"  상: 0.3"  폭: 12"    높: 0.6"   │
│ 폰트: 28pt, Bold, White                     │
│                                             │
│ [CONTENT AREA]                              │
│ 좌: 0.5"  상: 1.1"  폭: 12.3"  높: 5.9"   │
│ 폰트: 16pt, Regular, White/LightGray        │
│                                             │
└─────────────────────────────────────────────┘
```

플레이스홀더:
- `idx=0`: Title
- `idx=1`: Content (bullets, table, chart)

---

**레이아웃 4: Two Content (2분할)**

용도: 비교, 좌우 대조 슬라이드

```
┌─────────────────────────────────────────────┐
│ [TITLE]                                     │
│ 좌: 0.5"  상: 0.3"  폭: 12"    높: 0.6"   │
│                                             │
│ [LEFT CONTENT]      │ [RIGHT CONTENT]       │
│ 좌: 0.5"  상: 1.1"  │ 좌: 6.9"  상: 1.1"  │
│ 폭: 6.2"  높: 5.9"  │ 폭: 6.2"  높: 5.9"  │
│                     │                      │
│ [CENTER DIVIDER]    │                      │
│ 좌: 6.6"  상: 1.2"  폭: 0.04"  높: 5.6"   │
│ 색상: Accent2 (20% opacity)                 │
└─────────────────────────────────────────────┘
```

플레이스홀더:
- `idx=0`: Title
- `idx=1`: Left Content
- `idx=2`: Right Content

---

**레이아웃 5: Comparison (비교 카드)**

용도: 항목 대 항목 비교 (A vs B)

```
┌─────────────────────────────────────────────┐
│ [TITLE]  0.5" / 0.3" / 12" / 0.6"          │
│                                             │
│ ┌──────────────┐    ┌──────────────────┐   │
│ │ [LEFT LABEL] │    │  [RIGHT LABEL]   │   │
│ │ 0.5"/1.1"    │    │  6.9"/1.1"       │   │
│ │ 폰트: 14pt   │    │  폰트: 14pt      │   │
│ │ Accent 배경  │    │  Accent2 배경    │   │
│ ├──────────────┤    ├──────────────────┤   │
│ │ [LEFT BODY]  │    │  [RIGHT BODY]    │   │
│ │ 0.5"/1.6"    │    │  6.9"/1.6"       │   │
│ │ 높: 4.8"     │    │  높: 4.8"        │   │
│ └──────────────┘    └──────────────────┘   │
└─────────────────────────────────────────────┘
```

플레이스홀더:
- `idx=0`: Title
- `idx=1`: Left Label
- `idx=2`: Left Body
- `idx=3`: Right Label
- `idx=4`: Right Body

---

**레이아웃 6: Blank (여백/자유 배치)**

용도: 인포그래픽, 다이어그램, 전면 이미지

```
┌─────────────────────────────────────────────┐
│                                             │
│   (플레이스홀더 없음, 전체 배경만 설정)        │
│                                             │
│   python-pptx로 자유 오브젝트 배치           │
│                                             │
└─────────────────────────────────────────────┘
```

플레이스홀더: 없음 (python-pptx로 직접 배치)

---

### 2.2 색상 팔레트 시스템

#### 구조 원칙

색상은 `themes/` 디렉토리의 YAML/JSON 파일로 분리하고, 파이프라인 실행 시 테마 이름을 인자로 전달하는 방식으로 전환.

```
themes/
  dark.yaml        # 현재 기본 (개선판)
  light.yaml       # 라이트/비즈니스 테마
  brand-luxury.yaml  # 프리미엄 수입차 브랜드 테마
```

#### 테마 1: Dark (기본, 현재 것 개선)

```yaml
# themes/dark.yaml
name: dark
display_name: "다크 (기본)"

background:
  primary:   "#0F0F1A"    # 현재 #1A1A2E보다 더 깊은 네이비블랙
  secondary: "#141428"    # 카드/섹션 배경
  surface:   "#1E1E35"    # 테이블 행, 코드블록 배경

text:
  primary:   "#F5F5FA"    # 순백보다 살짝 따뜻한 흰색
  secondary: "#9A9AB0"    # 설명, 부제목
  muted:     "#5C5C78"    # 캡션, 날짜

accent:
  primary:   "#00C8F0"    # 시안 (현재 #00D2FF, 채도 약간 하향)
  secondary: "#6D28D9"    # 보라 (현재 #7C3AED, 채도 정비)
  tertiary:  "#059669"    # 에메랄드 (현재 #10B981)
  warning:   "#F59E0B"    # 앰버 (경고/주목)
  danger:    "#EF4444"    # 레드 (위험/부정)

brand:
  n8n:       "#EA4B71"    # n8n 핑크 (유지)

chart:
  series: ["#00C8F0", "#6D28D9", "#059669", "#F59E0B", "#EF4444"]
  grid:   "#2A2A45"
  axis:   "#5C5C78"
```

#### 테마 2: Light (비즈니스/인쇄용)

```yaml
# themes/light.yaml
name: light
display_name: "라이트 (비즈니스)"

background:
  primary:   "#FAFAFA"    # 오프화이트 (순백 아님)
  secondary: "#F0F0F5"    # 카드 배경
  surface:   "#E8E8F0"    # 테이블 행, 구분선

text:
  primary:   "#1A1A2E"    # 다크 테마의 배경색을 텍스트로 재활용 (일관성)
  secondary: "#4A4A6A"    # 설명
  muted:     "#8A8AA0"    # 캡션

accent:
  primary:   "#0077B6"    # 딥 블루 (시안의 인쇄 친화 버전)
  secondary: "#5B21B6"    # 딥 퍼플
  tertiary:  "#047857"    # 딥 그린
  warning:   "#D97706"    # 딥 앰버
  danger:    "#DC2626"    # 딥 레드

brand:
  n8n:       "#C9275A"    # n8n 핑크 진하게 (인쇄용)

chart:
  series: ["#0077B6", "#5B21B6", "#047857", "#D97706", "#DC2626"]
  grid:   "#D0D0E0"
  axis:   "#8A8AA0"
```

#### 테마 3: Brand Luxury (프리미엄 수입차)

```yaml
# themes/brand-luxury.yaml
name: brand-luxury
display_name: "럭셔리 브랜드"

background:
  primary:   "#0A0A0A"    # 거의 순흑 (프리미엄)
  secondary: "#111118"
  surface:   "#1A1A22"

text:
  primary:   "#F0EAD6"    # 따뜻한 크림화이트 (럭셔리 느낌)
  secondary: "#A09070"    # 골드브라운
  muted:     "#5A5040"

accent:
  primary:   "#C5A028"    # 골드 (브랜드 프리미엄)
  secondary: "#8A7A50"    # 브론즈
  tertiary:  "#4A8A6A"    # 딥 그린 (자동차 브랜드 색상 연상)
  warning:   "#C87020"    # 앰버 골드
  danger:    "#A03030"    # 딥 레드

brand:
  n8n:       "#EA4B71"

chart:
  series: ["#C5A028", "#8A7A50", "#4A8A6A", "#C87020", "#A03030"]
  grid:   "#2A2A18"
  axis:   "#5A5040"
```

#### 커스텀 브랜드 컬러 주입 방법

```python
# 사용 예시 (파이프라인 진입점)
python create_slides.py \
  --theme dark \
  --brand-color "#EA4B71" \
  --accent-override "#00C8F0"

# 또는 YAML 오버라이드
python create_slides.py --theme dark --theme-override custom.yaml
```

`custom.yaml`은 변경하고 싶은 키만 포함 (나머지는 베이스 테마에서 상속).

---

### 2.3 타이포그래피

#### 문제 진단

현재 `Apple SD Gothic Neo`는 macOS 전용. Windows에서 PPTX 파일을 열면 폰트 치환 발생 → 레이아웃 붕괴 위험.

#### 추천 폰트 스택

| 용도 | 추천 폰트 | 대체 (Fallback) | 이유 |
|------|-----------|-----------------|------|
| 한글 제목 | **Noto Sans KR** | 맑은 고딕, 본고딕 | 구글 폰트, 크로스플랫폼, 무료, 기술 발표에 어울리는 모던한 획 |
| 한글 본문 | **Noto Sans KR** | 맑은 고딕 | 동일 패밀리로 일관성 유지 |
| 영문 제목 | **DM Sans** | Outfit, Poppins | 기하학적 산세리프. Noto와 혼용 시 획 무게 잘 맞음 |
| 영문 강조 | **DM Mono** | JetBrains Mono | 코드블록, 수치, 인용 모노스페이스 |
| 장식용 | **Bebas Neue** (선택) | Impact | 대형 숫자, 타이틀 오버레이에만 사용 |

**금지 폰트 (AI 슬로프 시그니처):** Arial, Calibri, Roboto, Inter, System Font

#### 크기 체계 (타입 스케일)

```
타입 스케일 (베이스: 16pt)

Title Slide 메인   : 48pt  Bold     (3.0× base)
Title Slide 부제목 : 28pt  Regular  (1.75×)
섹션 넘버          : 14pt  SemiBold (0.875×)  — Uppercase + Letter-spacing 0.2em
섹션 제목          : 40pt  Bold     (2.5×)
슬라이드 제목      : 28pt  Bold     (1.75×)
본문 (콘텐츠)      : 16pt  Regular  (1.0×)
본문 강조          : 16pt  SemiBold (1.0×)
표 헤더            : 14pt  SemiBold (0.875×)
표 본문            : 13pt  Regular  (0.8125×)
캡션/메타          : 12pt  Regular  (0.75×)
코드/모노          : 14pt  Regular  (0.875×) — DM Mono
대형 수치 (인포)   : 64pt  Bold     (4.0×)   — Bebas Neue
```

#### 줄 간격 및 여백

```
줄 간격 (Line Height):
  제목류   : 1.1 (타이트)
  본문     : 1.5 (읽기 편안)
  표       : 1.3

단락 간격 (Space After):
  본문 단락: 8pt
  불릿 항목: 6pt
  표 행    : 0pt (셀 패딩으로 처리)

셀 패딩 (표):
  상하: 6pt / 좌우: 8pt
```

---

### 2.4 시각적 요소

#### 차트/다이어그램 스타일 가이드

**원칙:** python-pptx의 기본 차트 스타일을 쓰지 않는다. 모든 시각화는 다음 두 방법 중 하나로 처리.

1. **텍스트 다이어그램 (ASCII/박스):** 마크다운 코드블록에 작성 → 슬라이드에서 모노스페이스 폰트 영역으로 표현. 현재 `presentation.md`에 이미 이 방식 사용 중.

2. **python-pptx 직접 그리기:** 박스, 화살표, 레이블을 도형으로 배치. `add_shape` + `add_text` 조합.

**차트 색상 규칙:**
- 계열 색상: 테마의 `chart.series` 배열 순서 적용
- 그리드 선: `chart.grid` (희미하게)
- 축 라벨: `chart.axis` 색상, 12pt
- 배경: 투명 (슬라이드 배경이 비침)
- 범례: 슬라이드 우측 하단, 12pt

**피해야 할 차트 스타일:**
- 3D 효과, 그림자, 베벨
- 기본 Office 파란색 단색 차트
- 지나치게 많은 계열 (5개 이상)

#### 다이어그램 컴포넌트 (python-pptx)

```
노드 박스:
  크기: 폭 2.0" × 높 0.6" (기본)
  테두리 반경: 0.1" (rounded rectangle)
  배경: BG_SURFACE
  테두리: Accent1 (1pt)
  텍스트: 14pt, Center, White

화살표:
  선 색상: Accent1
  선 두께: 1.5pt
  화살촉: 단방향 열린 화살촉

강조 노드:
  배경: Accent1 (20% 불투명도)
  테두리: Accent1 (2pt)
  텍스트: Accent1, Bold

구분선:
  색상: Accent2 (30% 불투명도)
  선 두께: 0.5pt
  스타일: 실선
```

#### 아이콘 사용 전략

현재 `create_slides.py`에는 아이콘이 없다. 단기적으로는 유니코드 이모지를 텍스트로 사용하는 방식이 가장 구현이 쉽다. 단 발표용 PPTX에서 이모지 렌더링은 OS별 차이가 있으므로 주의.

**권장 방식 (우선순위 순):**

1. **유니코드 기호:** ✓ ✗ → ↑ ↓ ● ○ ▶ ── 등. 폰트 독립적.
2. **이모지 (제한적):** 색상 이모지는 타이틀/강조에만. 본문 이모지 남용 금지.
3. **SVG to EMF 변환:** 외부 아이콘을 EMF로 변환 후 삽입 (FE-012 태스크).

#### 여백/그리드 시스템

```
슬라이드 마진 (safe zone):
  좌: 0.5"  우: 0.5"  상: 0.3"  하: 0.3"

콘텐츠 영역:
  좌: 0.5"  우: 12.833"  (폭 12.333")
  상: 1.0"  하: 7.2"     (높 6.2"  — 제목 아래)

타이틀 영역:
  상: 0.3"  높: 0.6"

구분선 (타이틀 하단):
  상: 0.92"  높: 0.04"

칼럼 그리드 (12칼럼 기준):
  1칼럼 폭: 12.333" / 12 ≈ 1.028"
  거터: 0.2" (칼럼 사이 간격)

2분할 레이아웃:
  좌 패널: 좌 0.5", 폭 6.0"
  우 패널: 좌 6.833", 폭 6.0"
  가운데 여백: 0.333"

3분할 레이아웃:
  패널 폭: 3.944"
  거터: 0.2"
```

---

## 3. 마크다운 보고서 템플릿 디자인

### 3.1 파일 구조 (Jinja2 템플릿)

```
templates/
  report.md.j2          # 보고서 마크다운 메인 템플릿
  slides-metadata.yaml.j2  # pandoc 메타데이터 (슬라이드 변환용)
  sections/
    title.md.j2           # 타이틀 섹션
    toc.md.j2             # 목차
    content.md.j2         # 일반 콘텐츠 섹션
    conclusion.md.j2      # 결론 섹션
    references.md.j2      # 참고자료
```

### 3.2 보고서 마크다운 시각적 구조

GitHub 마크다운 렌더링 기준. 인쇄 및 PDF 변환도 고려.

#### 최상위 구조

```markdown
# {title}

> {subtitle}
> {date} | {audience} | {duration}

---

## 목차

{toc_items}

---

## {section_number}. {section_title}

> **{section_type}** — {section_summary}

{content}

---

## 참고 자료

{references}
```

#### 강조 블록 패턴

| 블록 유형 | 마크다운 표현 | 용도 |
|-----------|---------------|------|
| **핵심 인사이트** | `> **💡 핵심:**` | 단락 내 핵심 메시지 |
| **데이터 포인트** | `> 📊 {수치} — {설명}` | 통계, 수치 강조 |
| **인용문** | `> "인용" — *출처* ` | 유명 발언, 정의 |
| **경고/주의** | `> ⚠️ **주의:**` | 리스크, 한계 |
| **실행 항목** | `> ✅ **액션:**` | 다음 단계, TO-DO |
| **용어 설명** | `> 💡 **{용어}** = {설명}` | 비개발자용 용어 |

#### 표 스타일 가이드

표는 최대 4~5열로 제한. 열이 많을수록 PPTX 변환 시 텍스트가 잘림.

```markdown
| 항목 | 값 | 설명 |
|:-----|:--:|:-----|
| **강조 항목** | 수치 | 설명 텍스트 |
```

**표 설계 원칙:**
- 첫 열: 왼쪽 정렬 (항목명)
- 수치 열: 가운데 정렬
- 설명 열: 왼쪽 정렬
- Bold 강조는 첫 열 핵심 항목에만 사용
- 표 위에 항상 1줄 설명 또는 제목 추가

#### 코드블록 스타일 가이드

```markdown
```언어명
코드 또는 다이어그램
```
```

**사용 원칙:**
- 언어명을 항상 명시 (`python`, `yaml`, `bash`, `text`, ``)
- ASCII 아트 다이어그램은 ` ` `` `text` `` ` 또는 언어 없이
- 코드블록은 가로로 넓게 쓰되 80자 이내 권장 (PPTX 슬라이드 변환 고려)
- 중요 구조 설명에는 `text` 타입으로 박스 다이어그램 사용

#### 다이어그램 전략 (Mermaid vs ASCII)

| 방식 | 장점 | 단점 | 권장 상황 |
|------|------|------|-----------|
| **Mermaid** | GitHub에서 자동 렌더링, 유지보수 쉬움 | PPTX 변환 미지원, Python 추가 의존성 | 보고서 단독 배포 시 |
| **ASCII 박스** | 어디서나 렌더링, PPTX 코드블록으로 직접 이전 | 복잡한 다이어그램 어려움 | PPTX 변환 포함 파이프라인 |
| **이미지 삽입** | 품질 최고 | 생성 자동화 어려움 | 최종 보고서 |

**현재 파이프라인 권장:** ASCII 박스 다이어그램 사용. 이유: PPTX 슬라이드로 직접 이전 가능하고 LLM이 생성하기 쉬움.

Mermaid는 보고서 HTML/PDF 렌더링 전용 파이프라인이 분리될 때 도입.

#### 인포그래픽 변환 마커

현재 `presentation.md`에 `> 인포그래픽 변환 예정` 주석이 있다. 이를 구조화된 마커로 표준화:

```markdown
<!-- INFOGRAPHIC: timeline -->
| 시기 | 사건 | 의미 |
|------|------|------|
| ... | ... | ... |
<!-- /INFOGRAPHIC -->
```

파이프라인이 이 마커를 감지하면 해당 섹션을 `Blank` 레이아웃 슬라이드로 분류하고 python-pptx 커스텀 렌더러를 호출.

---

## 4. 프론트/테마 개발 태스크 목록

### 분류 A: reference.pptx 테마 파일 제작

---

**FE-001: reference.pptx 기본 다크 테마 제작**

- **제목:** pandoc 변환용 reference.pptx 다크 테마 파일 생성
- **설명:** pandoc이 마크다운을 PPTX로 변환할 때 기준으로 사용하는 `reference.pptx` 파일을 python-pptx로 생성. 슬라이드 레이아웃 6종, 색상, 폰트를 다크 테마 스펙에 맞게 설정.
- **의존성:** 없음 (최우선)
- **복잡도:** L
- **수용 기준:**
  - [ ] `templates/reference-dark.pptx` 파일이 생성됨
  - [ ] 레이아웃 6종 (Title Slide, Section Header, Title and Content, Two Content, Comparison, Blank) 포함
  - [ ] 각 레이아웃의 플레이스홀더 위치/크기가 2.1절 스펙과 일치
  - [ ] pandoc 명령 `pandoc input.md -t pptx --reference-doc=templates/reference-dark.pptx -o output.pptx` 실행 시 오류 없음
  - [ ] 생성된 PPTX를 LibreOffice Impress에서 열었을 때 레이아웃이 깨지지 않음

---

**FE-002: 슬라이드 마스터 배경 및 데코 요소 설정**

- **제목:** 슬라이드 마스터에 배경색, 헤더 룰, 푸터 라인 자동 적용
- **설명:** 모든 슬라이드에 공통으로 적용되는 배경색, 타이틀 하단 구분선(accent rule), 슬라이드 번호 위치를 마스터 레벨에서 설정. 현재는 각 슬라이드에 `set_bg()`를 반복 호출하는 구조를 마스터로 이전.
- **의존성:** FE-001
- **복잡도:** M
- **수용 기준:**
  - [ ] 슬라이드 마스터에 `BG_DARK` 배경색 적용
  - [ ] 타이틀 레이아웃에 accent 구분선이 마스터 레벨에서 그려짐
  - [ ] 슬라이드 번호가 우측 하단에 표시됨 (12pt, LightGray)
  - [ ] 새 슬라이드 추가 시 `set_bg()` 호출 없이도 배경이 적용됨

---

**FE-003: 라이트 테마 reference.pptx 제작**

- **제목:** 비즈니스/인쇄용 라이트 테마 reference.pptx 생성
- **설명:** FE-001의 다크 테마와 동일한 레이아웃 구조를 유지하면서, 2.2절 Light 테마 색상을 적용한 별도 reference 파일 생성. `--theme light` 인자로 선택 가능.
- **의존성:** FE-001, FE-007 (테마 설정 시스템)
- **복잡도:** S
- **수용 기준:**
  - [ ] `templates/reference-light.pptx` 파일이 생성됨
  - [ ] 라이트 테마 색상 팔레트 (2.2절) 적용
  - [ ] 다크 테마와 레이아웃 구조 동일
  - [ ] 흑백 인쇄 시 텍스트 가독성 확보 (배경/텍스트 명암비 4.5:1 이상)

---

### 분류 B: 색상 팔레트/테마 설정 시스템

---

**FE-004: 테마 YAML 파일 구조 설계 및 파서 구현**

- **제목:** `themes/*.yaml` 파일 로더 및 RGBColor 변환 유틸리티 구현
- **설명:** 현재 `create_slides.py` 상단의 전역 색상 상수를 YAML 파일 기반 테마 시스템으로 교체. `ThemeLoader` 클래스 또는 함수가 YAML을 로드하고 python-pptx `RGBColor` 객체로 변환하는 딕셔너리를 반환.
- **의존성:** 없음
- **복잡도:** S
- **수용 기준:**
  - [ ] `themes/dark.yaml`, `themes/light.yaml`, `themes/brand-luxury.yaml` 파일 생성
  - [ ] `load_theme(name: str) -> dict` 함수 구현
  - [ ] 반환 딕셔너리가 `theme['accent']['primary']` 형태로 `RGBColor` 객체 포함
  - [ ] 존재하지 않는 테마 이름 전달 시 명확한 오류 메시지
  - [ ] YAML 오버라이드 (`--theme-override custom.yaml`) 지원: 지정된 키만 베이스 테마에 덮어씌움

---

**FE-005: CLI 인자 파서 구현 (`argparse`)**

- **제목:** `create_slides.py`에 CLI 인자 파서 추가
- **설명:** `python create_slides.py --theme dark --output output.pptx --input presentation.md` 형태로 실행할 수 있도록 `argparse` 기반 CLI 인터페이스 추가. 현재는 인자가 없어 파일명과 테마가 하드코딩됨.
- **의존성:** FE-004
- **복잡도:** S
- **수용 기준:**
  - [ ] `--theme {dark|light|brand-luxury}` 인자로 테마 선택 가능
  - [ ] `--input` 인자로 입력 마크다운 파일 경로 지정
  - [ ] `--output` 인자로 출력 PPTX 파일 경로 지정
  - [ ] `--theme-override` 인자로 YAML 오버라이드 파일 지정
  - [ ] `--help` 출력 시 각 인자 설명 포함
  - [ ] 기본값: `--theme dark`, `--output output.pptx`

---

**FE-006: 테마 적용 헬퍼 함수 리팩토링**

- **제목:** `add_text`, `add_shape` 등 헬퍼 함수에 테마 컨텍스트 주입
- **설명:** 현재 헬퍼 함수들이 `WHITE`, `ACCENT` 등 전역 상수를 직접 참조. 테마 시스템 도입 후에는 `theme` 딕셔너리를 컨텍스트로 받아 색상을 결정하도록 리팩토링. 전역 상태 의존성 제거.
- **의존성:** FE-004, FE-005
- **복잡도:** M
- **수용 기준:**
  - [ ] 모든 헬퍼 함수가 전역 색상 상수 직접 참조 제거
  - [ ] `theme: dict` 파라미터 또는 모듈 수준 `set_active_theme(theme)` 패턴 사용
  - [ ] 기존 슬라이드 생성 결과와 시각적으로 동일한 출력 (회귀 없음)
  - [ ] 타입 힌트 추가

---

**FE-007: 폰트 크로스플랫폼 해결 (Noto Sans KR 적용)**

- **제목:** Apple SD Gothic Neo 의존성 제거, Noto Sans KR로 교체
- **설명:** 현재 폰트를 크로스플랫폼 폰트로 교체. Noto Sans KR은 Google Fonts에서 무료 다운로드 가능. 폰트가 시스템에 설치되지 않은 경우를 위한 폴백 로직 추가.
- **의존성:** FE-006
- **복잡도:** S
- **수용 기준:**
  - [ ] 모든 `font_name="Apple SD Gothic Neo"` 참조를 `"Noto Sans KR"`로 교체
  - [ ] `themes/*.yaml`에 `typography.font_korean`, `typography.font_latin`, `typography.font_mono` 키 추가
  - [ ] `check_fonts()` 함수로 실행 전 폰트 설치 여부 확인
  - [ ] 폰트 미설치 시 경고 메시지 + 폴백 폰트 (`맑은 고딕` → `Arial`) 자동 적용
  - [ ] Windows 환경에서 생성된 PPTX가 정상 렌더링됨 (LibreOffice 검증)

---

### 분류 C: Jinja2 마크다운 템플릿 디자인

---

**FE-008: 보고서 마크다운 Jinja2 기본 템플릿 작성**

- **제목:** `templates/report.md.j2` 메인 보고서 템플릿 생성
- **설명:** LLM이 생성한 콘텐츠(JSON 또는 구조화된 딕셔너리)를 받아 3.1절 구조의 마크다운 보고서를 렌더링하는 Jinja2 템플릿. 섹션 반복, 표 생성, 인용 블록 등을 포함.
- **의존성:** 없음
- **복잡도:** M
- **수용 기준:**
  - [ ] `templates/report.md.j2` 파일 생성
  - [ ] 템플릿 변수: `title`, `subtitle`, `date`, `audience`, `duration`, `sections[]`, `references[]`
  - [ ] 각 섹션 변수: `number`, `title`, `type`, `summary`, `content`, `infographic_type` (optional)
  - [ ] `render_report(data: dict) -> str` 함수 구현
  - [ ] 렌더링 결과가 GitHub 마크다운에서 깨지지 않음
  - [ ] `presentation.md`를 이 템플릿으로 재생성 가능함 (역호환성 검증)

---

**FE-009: 섹션별 서브 템플릿 작성**

- **제목:** `templates/sections/` 하위 섹션 템플릿 모음 작성
- **설명:** 섹션 유형(용어 설명, 타임라인, 비교표, 결론 등)에 따라 다른 마크다운 구조가 적용되도록 섹션별 Jinja2 서브 템플릿 작성.
- **의존성:** FE-008
- **복잡도:** M
- **수용 기준:**
  - [ ] `glossary.md.j2`: 용어 설명 표 (3열: 용어, 영문, 설명)
  - [ ] `timeline.md.j2`: 타임라인 표 (시기, 사건, 의미) + `<!-- INFOGRAPHIC: timeline -->` 마커
  - [ ] `comparison.md.j2`: 비교 표 (다중 열)
  - [ ] `bullets.md.j2`: 불릿 리스트 섹션
  - [ ] `conclusion.md.j2`: 결론 + 다음 스텝 표
  - [ ] 각 서브 템플릿을 `{% include %}` 또는 `{% macro %}`로 메인 템플릿에서 호출 가능

---

**FE-010: INFOGRAPHIC 마커 파서 구현**

- **제목:** 마크다운의 `<!-- INFOGRAPHIC: type -->` 마커 감지 및 라우팅
- **설명:** 3.2절의 `<!-- INFOGRAPHIC -->` 마커를 파싱하여 해당 섹션을 적절한 python-pptx 렌더러로 라우팅하는 파서 구현. 타입별 렌더러 디스패치 테이블 설계.
- **의존성:** FE-008
- **복잡도:** M
- **수용 기준:**
  - [ ] `parse_infographic_markers(markdown_text: str) -> list[InfographicBlock]` 함수 구현
  - [ ] `InfographicBlock`: `type`, `content`, `position` 필드 포함
  - [ ] 지원 타입: `timeline`, `chart-bar`, `comparison`, `flow-diagram`, `stat-grid`
  - [ ] 미지원 타입 전달 시 `text` 코드블록으로 폴백
  - [ ] 마커 없는 일반 마크다운에서도 정상 동작

---

### 분류 D: 커스텀 슬라이드 컴포넌트 (python-pptx)

---

**FE-011: 슬라이드 컴포넌트 추상화 레이어 구현**

- **제목:** 슬라이드 유형별 컴포넌트 클래스 설계 및 기본 클래스 구현
- **설명:** 현재 각 슬라이드가 인라인 코드로 작성되어 있는 구조를 `TitleSlide`, `SectionSlide`, `ContentSlide`, `ComparisonSlide`, `InfographicSlide` 컴포넌트 클래스로 추상화. 각 컴포넌트는 `render(prs: Presentation, data: dict, theme: dict) -> None` 인터페이스를 구현.
- **의존성:** FE-006, FE-007
- **복잡도:** L
- **수용 기준:**
  - [ ] `components/` 디렉토리에 각 컴포넌트 모듈 생성
  - [ ] 공통 베이스 클래스 `SlideComponent` 구현 (공통 헬퍼 포함)
  - [ ] `TitleSlide`, `SectionSlide`, `ContentSlide`, `ComparisonSlide`, `BlankSlide` 구현
  - [ ] 각 컴포넌트가 현재 `create_slides.py`의 대응 슬라이드와 시각적으로 동일한 출력 생성
  - [ ] 컴포넌트 레지스트리 `SLIDE_REGISTRY: dict[str, type[SlideComponent]]` 구현

---

**FE-012: 타임라인 인포그래픽 슬라이드 컴포넌트**

- **제목:** `TimelineSlide` 컴포넌트 구현 (수평 타임라인)
- **설명:** `presentation.md`의 "최근 1년 타임라인" 섹션을 텍스트 표 대신 수평 타임라인 인포그래픽으로 렌더링하는 컴포넌트. 연도/분기별 노드, 사건 텍스트, 연결선을 python-pptx 도형으로 그림.
- **의존성:** FE-011
- **복잡도:** L
- **수용 기준:**
  - [ ] 최대 12개 이벤트를 수평 타임라인으로 배치
  - [ ] 노드: 원형 도형, 날짜 레이블, 사건 요약 텍스트
  - [ ] 연결선: Accent1 색상 수평선
  - [ ] 짝수/홀수 이벤트를 선 위/아래로 교차 배치 (지그재그 패턴)
  - [ ] 입력 데이터 형식: `[{"date": "2024.11", "event": "MCP 발표", "meaning": "..."}]`
  - [ ] 텍스트가 슬라이드 경계를 벗어나지 않음

---

**FE-013: 통계 그리드 슬라이드 컴포넌트**

- **제목:** `StatGridSlide` 컴포넌트 구현 (KPI/수치 강조)
- **설명:** 대형 수치와 설명 텍스트를 그리드로 배치하는 컴포넌트. n8n 성장 지표, 시장 규모 수치 등을 시각적으로 강조.
- **의존성:** FE-011
- **복잡도:** M
- **수용 기준:**
  - [ ] 2×2, 2×3, 3×2 그리드 레이아웃 지원
  - [ ] 각 셀: 대형 수치(48pt, Accent 색상) + 단위 레이블(18pt) + 설명(14pt, LightGray)
  - [ ] 셀 배경: BG_SURFACE, 테두리 없음, 충분한 내부 패딩
  - [ ] 입력 형식: `[{"value": "$2.5B", "unit": "밸류에이션", "desc": "Series C 기준"}]`
  - [ ] Bebas Neue 또는 DM Sans Bold로 수치 렌더링

---

**FE-014: AI 진화 단계 다이어그램 슬라이드 컴포넌트**

- **제목:** `EvolutionDiagramSlide` 컴포넌트 구현 (수직 진화 단계)
- **설명:** `presentation.md` 6-5절의 "AI 5세대 진화" 다이어그램을 현재 ASCII 박스에서 시각적 도형 다이어그램으로 업그레이드. 각 세대를 박스로 표현하고 화살표로 연결.
- **의존성:** FE-011
- **복잡도:** M
- **수용 기준:**
  - [ ] 최대 6단계의 수직 진화 다이어그램 렌더링
  - [ ] 각 단계: 번호 배지 + 제목 + 연도 + 설명 텍스트
  - [ ] 현재 단계 강조: Accent 색상 배경, 텍스트 Bold
  - [ ] 단계 간 화살표: Accent1 색상, 단방향
  - [ ] 슬라이드 좌우 2분할: 왼쪽 다이어그램, 오른쪽 보충 설명

---

**FE-015: 프레임워크 비교 카드 컴포넌트**

- **제목:** `FrameworkComparisonSlide` 컴포넌트 구현
- **설명:** AI 에이전트 프레임워크 비교 (LangGraph, CrewAI, OpenAI SDK, n8n 등)를 난이도 색상 배지와 함께 카드 형식으로 렌더링. 현재 텍스트 표를 시각적 카드 레이아웃으로 업그레이드.
- **의존성:** FE-011
- **복잡도:** M
- **수용 기준:**
  - [ ] 최대 5개 프레임워크를 수평 카드 레이아웃으로 배치
  - [ ] 각 카드: 프레임워크명(Bold) + 접근 방식 + 적합 대상 + 난이도 배지
  - [ ] 난이도 배지: 🔴/🟡/🟢 대신 Danger/Warning/Success 색상 원형 도형 사용
  - [ ] n8n 카드는 Accent 색상 테두리로 강조 (Sweet Spot 표시)
  - [ ] 카드 간 균등 간격 배치

---

**FE-016: 멀티 에이전트 아키텍처 다이어그램 컴포넌트**

- **제목:** `MultiAgentDiagramSlide` 컴포넌트 구현
- **설명:** `presentation.md` 6-6절의 싱글/멀티 에이전트 비교 다이어그램을 도형으로 구현. 오케스트레이터 노드와 전문 에이전트 노드를 트리 구조로 렌더링.
- **의존성:** FE-011
- **복잡도:** L
- **수용 기준:**
  - [ ] 싱글 에이전트 (좌) vs 멀티 에이전트 (우) 2분할 레이아웃
  - [ ] 멀티 에이전트: 오케스트레이터 노드 (Accent 강조) + 하위 전문 에이전트 노드들 + 연결선
  - [ ] 노드: 둥근 사각형, 텍스트 레이블
  - [ ] 성과 차이 수치 (싱글 1.7% vs 멀티 100%) 하단에 강조 표시
  - [ ] 최대 6개 하위 에이전트 지원

---

### 분류 E: 파이프라인 통합

---

**FE-017: 마크다운 → PPTX 파이프라인 통합 진입점**

- **제목:** `pipeline.py` 통합 실행 스크립트 구현
- **설명:** 마크다운 파일을 입력받아 (1) Jinja2 렌더링, (2) INFOGRAPHIC 마커 파싱, (3) 섹션별 컴포넌트 디스패치, (4) PPTX 출력 순서로 실행하는 통합 진입점 스크립트.
- **의존성:** FE-005, FE-008, FE-010, FE-011
- **복잡도:** M
- **수용 기준:**
  - [ ] `python pipeline.py --input presentation.md --theme dark --output output.pptx` 명령 한 줄로 실행
  - [ ] 실행 중 진행 상황 로그 출력 (`[1/4] 마크다운 파싱 중...` 형식)
  - [ ] 오류 발생 시 어느 섹션에서 실패했는지 명확한 오류 메시지
  - [ ] `--dry-run` 플래그: PPTX 생성 없이 슬라이드 구조만 출력
  - [ ] 생성 완료 후 슬라이드 수, 소요 시간, 출력 파일 경로 요약 출력

---

**FE-018: 슬라이드 썸네일 미리보기 생성 (선택)**

- **제목:** 생성된 PPTX의 슬라이드별 PNG 썸네일 생성
- **설명:** `--preview` 플래그 사용 시 LibreOffice 또는 `python-pptx` + Pillow를 활용해 슬라이드별 PNG 썸네일을 `previews/` 디렉토리에 저장. 비개발자가 터미널 없이도 결과를 확인할 수 있도록.
- **의존성:** FE-017
- **복잡도:** M
- **수용 기준:**
  - [ ] `python pipeline.py --input ... --preview` 실행 시 `previews/slide_XX.png` 파일 생성
  - [ ] 썸네일 크기: 1333×750px (원본 비율 유지)
  - [ ] LibreOffice 없는 환경에서는 경고 메시지 후 스킵
  - [ ] `previews/index.html`에 모든 썸네일을 그리드로 나열한 HTML 파일 생성

---

### 태스크 우선순위 요약

| 단계 | 태스크 | 이유 |
|------|--------|------|
| **1단계 (즉시)** | FE-004, FE-005, FE-007 | 테마 시스템 기반, 폰트 크로스플랫폼 해결 |
| **2단계 (핵심)** | FE-001, FE-006, FE-008, FE-011 | reference.pptx + 컴포넌트 추상화 |
| **3단계 (기능)** | FE-002, FE-003, FE-009, FE-010, FE-017 | 파이프라인 완성 |
| **4단계 (인포그래픽)** | FE-012, FE-013, FE-014, FE-015, FE-016 | 시각적 업그레이드 |
| **5단계 (UX)** | FE-018 | 비개발자 편의 기능 |

---

*문서 끝. 최종 업데이트: 2026-03-12*
