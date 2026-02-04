from __future__ import annotations

import html
import re
from typing import Callable, Optional

from markdown import markdown as md_to_html
import streamlit as st

PLACEHOLDER_TOKEN = "{{chart}}"
PLACEHOLDER_ENCODINGS = [
    "&#123;&#123;chart&#125;&#125;",
    "&lbrace;&lbrace;chart&rbrace;&rbrace;",
    "{{ chart }}",
]
PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*(?:chart|viz)(?:\s*:\s*([a-zA-Z0-9_\-]+))?\s*\}\}", re.IGNORECASE)
ENCODED_PATTERN = re.compile(
    r"(&#123;|&lbrace;)\s*(&#123;|&lbrace;)\s*(?:chart|viz)(?:\s*:\s*([a-zA-Z0-9_\-]+))?\s*(&#125;|&rbrace;)\s*(&#125;|&rbrace;)",
    re.IGNORECASE,
)


def _normalise_placeholders(content: str) -> str:
    def _replace_encoded(match: re.Match[str]) -> str:
        chart_id = match.group(3)
        if chart_id:
            return f"{{{{chart:{chart_id}}}}}"
        return PLACEHOLDER_TOKEN

    result = ENCODED_PATTERN.sub(_replace_encoded, content)
    for token in PLACEHOLDER_ENCODINGS:
        result = result.replace(token, PLACEHOLDER_TOKEN)
    # Unescape any HTML entities within placeholders
    return html.unescape(result)


def _split_segments(content: str) -> list[tuple[str, Optional[str]]]:
    segments: list[tuple[str, Optional[str]]] = []
    last_index = 0
    for match in PLACEHOLDER_PATTERN.finditer(content):
        start, end = match.span()
        if start > last_index:
            segments.append(("text", content[last_index:start]))
        chart_id = match.group(1)
        if chart_id:
            chart_id = chart_id.strip()
        segments.append(("chart", chart_id))
        last_index = end
    if last_index < len(content):
        segments.append(("text", content[last_index:]))
    if not segments:
        segments.append(("text", content))
    return segments


def render_story_content(
    content: str,
    *,
    content_format: str = "markdown",
    chart_renderer: Optional[Callable[[Optional[str]], Optional[bool]]] = None,
) -> None:
    if not content.strip() and not chart_renderer:
        return

    normalised = _normalise_placeholders(content)
    segments = _split_segments(normalised)

    for kind, payload in segments:
        if kind == "text":
            segment = payload or ""
            if segment.strip():
                if content_format == "html":
                    html = segment
                else:
                    html = md_to_html(segment, extensions=["tables", "fenced_code"])
                st.markdown(f"<div class='story-content'>{html}</div>", unsafe_allow_html=True)
        elif kind == "chart":
            if chart_renderer:
                chart_renderer(payload)
