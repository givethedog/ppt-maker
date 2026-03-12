"""커스텀 Jinja2 필터.

마크다운 생성에 유용한 필터: md_table, md_bullet, slide_hint.
"""

from __future__ import annotations

import unicodedata


def _east_asian_width(text: str) -> int:
    """유니코드 동아시아 너비를 고려한 문자열 길이."""
    width = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        width += 2 if eaw in ("F", "W") else 1
    return width


def _pad_cell(text: str, width: int) -> str:
    """동아시아 문자 너비를 고려하여 셀 텍스트를 패딩."""
    current = _east_asian_width(text)
    padding = max(0, width - current)
    return text + " " * padding


def md_table(data: list[dict[str, str]]) -> str:
    """딕셔너리 리스트를 마크다운 표로 변환.

    >>> md_table([{"이름": "GPT-4", "회사": "OpenAI"}, {"이름": "Claude", "회사": "Anthropic"}])
    """
    if not data:
        return ""

    headers = list(data[0].keys())

    # 컬럼별 최대 너비 계산 (동아시아 문자 고려)
    col_widths = {}
    for h in headers:
        col_widths[h] = _east_asian_width(h)
    for row in data:
        for h in headers:
            val = str(row.get(h, ""))
            col_widths[h] = max(col_widths[h], _east_asian_width(val))

    # 헤더 행
    header_line = "| " + " | ".join(_pad_cell(h, col_widths[h]) for h in headers) + " |"
    # 구분선
    sep_line = "| " + " | ".join("-" * col_widths[h] for h in headers) + " |"
    # 데이터 행
    rows = []
    for row in data:
        cells = [_pad_cell(str(row.get(h, "")), col_widths[h]) for h in headers]
        rows.append("| " + " | ".join(cells) + " |")

    return "\n".join([header_line, sep_line, *rows])


def md_bullet(items: list[str], indent: int = 0) -> str:
    """리스트를 마크다운 불릿 리스트로 변환."""
    prefix = "  " * indent + "- "
    return "\n".join(prefix + item for item in items)


def slide_hint(slide_type: str, **kwargs: str) -> str:
    """슬라이드 변환 힌트 HTML 주석 생성.

    >>> slide_hint("timeline")
    '<!-- slide: type=timeline -->'
    """
    parts = [f"type={slide_type}"]
    for k, v in kwargs.items():
        parts.append(f"{k}={v}")
    return f"<!-- slide: {', '.join(parts)} -->"


# Jinja2 환경에 등록할 필터 딕셔너리
CUSTOM_FILTERS = {
    "md_table": md_table,
    "md_bullet": md_bullet,
    "slide_hint": slide_hint,
}
