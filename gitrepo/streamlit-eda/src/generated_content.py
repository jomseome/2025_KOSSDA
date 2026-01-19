from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "content" / "generated_content.json"


def _load_raw() -> Dict[str, Any]:
    if not OUTPUT_PATH.exists():
        return {"stories": {}}
    with OUTPUT_PATH.open("r", encoding="utf-8") as handle:
        data: Dict[str, Any] = json.load(handle)
    if "stories" in data:
        return data

    # Legacy single-story payload fallback
    legacy_title = data.get("title")
    slug = data.get("slug") or _suggest_slug(legacy_title or "story")
    story_payload = {
        "title": legacy_title or "데이터 스토리",
        "markdown": data.get("markdown", ""),
        "pdf_source": data.get("pdf_source"),
        "chart": data.get("chart"),
        "updated_at": data.get("saved_at"),
    }
    return {
        "stories": {slug: story_payload},
        "migrated_from_legacy": True,
        "updated_at": data.get("saved_at"),
    }


def _write_raw(payload: Dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _suggest_slug(value: str) -> str:
    base = re.sub(r"[^0-9a-zA-Z-]+", "-", value.strip().lower()).strip("-")
    base = base or "story"
    return base


def list_stories() -> Dict[str, str]:
    data = _load_raw()
    stories = data.get("stories", {})
    return {
        slug: (payload.get("title") or slug)
        for slug, payload in stories.items()
    }


def load_story(slug: str) -> Dict[str, Any] | None:
    data = _load_raw()
    stories = data.get("stories", {})
    return stories.get(slug)


def save_story(slug: str, payload: Dict[str, Any]) -> None:
    data = _load_raw()
    stories = data.setdefault("stories", {})
    story_payload = dict(payload)
    story_payload["updated_at"] = datetime.utcnow().isoformat()
    stories[slug] = story_payload
    data["updated_at"] = story_payload["updated_at"]
    _write_raw(data)


def ensure_unique_slug(candidate: str) -> str:
    base = _suggest_slug(candidate)
    data = _load_raw()
    stories = data.get("stories", {})
    if base not in stories:
        return base
    suffix = 2
    while f"{base}-{suffix}" in stories:
        suffix += 1
    return f"{base}-{suffix}"


def all_story_items() -> Iterable[Tuple[str, Dict[str, Any]]]:
    data = _load_raw()
    for slug, payload in data.get("stories", {}).items():
        yield slug, payload.copy()
