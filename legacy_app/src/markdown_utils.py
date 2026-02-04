from __future__ import annotations

import re
from textwrap import wrap
from typing import Iterable, List


def _clean_lines(raw_text: str) -> List[str]:
    text = raw_text.replace("\r", "\n")
    text = re.sub(r"\u00a0", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line]


def _chunk_sentences(sentences: Iterable[str], chunk_size: int = 3) -> List[str]:
    paragraphs: List[str] = []
    current: List[str] = []
    for sentence in sentences:
        if not sentence:
            continue
        current.append(sentence.strip())
        if len(current) >= chunk_size:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def auto_format_text(raw_text: str) -> str:
    """
    Convert raw PDF extracted text into a readable Markdown scaffold.

    This is a heuristic formatter that:
      * normalises spacing
      * converts ▪ markers into bullet points
      * groups remaining sentences into short paragraphs
    """

    lines = _clean_lines(raw_text)
    if not lines:
        return ""

    bullet_lines = [line.lstrip("▪").strip() for line in lines if line.startswith("▪")]
    other_lines = [line for line in lines if not line.startswith("▪")]

    joined = " ".join(other_lines)
    # Collapse multiple spaces and fix stray hyphenated numbers
    joined = re.sub(r"\s+", " ", joined)
    joined = re.sub(r"(\d)\s+(\d)", r"\1\2", joined)

    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Za-z가-힣0-9])", joined)
    paragraphs = _chunk_sentences(sentences, chunk_size=3)

    parts: List[str] = []
    if bullet_lines:
        parts.append("## 핵심 요약")
        for bullet in bullet_lines[:8]:
            parts.append(f"- {bullet}")
        parts.append("")

    if paragraphs:
        parts.append("## 상세 내용")
        for paragraph in paragraphs:
            parts.append(paragraph)

    formatted = "\n\n".join(part.strip() for part in parts if part.strip())
    return formatted.strip()
