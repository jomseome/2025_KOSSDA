import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

BASE = Path("content")
INDEX = BASE / "index.json"

def load_index() -> List[Dict]:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return []

def get_contents(category_key: str | None = None) -> List[Dict]:
    items = load_index()
    if category_key and category_key != "all":
        items = [i for i in items if i.get("category") == category_key]
    return items

def get_content(content_id: str) -> Optional[Dict]:
    for item in load_index():
        if item.get("id") == content_id:
            body_path = item.get("body")
            if body_path:
                p = BASE / body_path
                if p.exists():
                    item["body_text"] = p.read_text(encoding="utf-8")
            return item
    return None


_NON_WORD = re.compile(r"[^0-9a-zA-Z가-힣]+")


def _normalize_for_ngrams(text: str) -> str:
    cleaned = _NON_WORD.sub("", text.lower())
    return cleaned


def _extract_ngrams(text: str) -> set[str]:
    normalized = _normalize_for_ngrams(text)
    if not normalized:
        return set()
    grams: set[str] = set(normalized)
    if len(normalized) >= 2:
        grams.update(normalized[i : i + 2] for i in range(len(normalized) - 1))
    return grams


@lru_cache(maxsize=None)
def _read_body_cached(body_path: str | None) -> str:
    if not body_path:
        return ""
    path = BASE / body_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _item_field_ngrams(item: Dict) -> Dict[str, set[str]]:
    title_ngrams = _extract_ngrams(item.get("title", ""))
    summary_ngrams = _extract_ngrams(item.get("summary", ""))
    body_ngrams = _extract_ngrams(_read_body_cached(item.get("body")))
    return {
        "title": title_ngrams,
        "summary": summary_ngrams,
        "body": body_ngrams,
    }


def search_contents(query: str, category_key: str | None = None) -> List[Dict]:
    query = (query or "").strip()
    if not query:
        return get_contents(category_key)

    query_ngrams = _extract_ngrams(query)
    if not query_ngrams:
        return get_contents(category_key)

    items = get_contents(category_key)
    ranked: list[tuple[int, int, Dict]] = []
    for item in items:
        field_ngrams = _item_field_ngrams(item)
        title_score = len(query_ngrams & field_ngrams["title"])
        summary_score = len(query_ngrams & field_ngrams["summary"])
        body_score = len(query_ngrams & field_ngrams["body"])

        if title_score:
            ranked.append((0, -title_score, item))
        elif summary_score:
            ranked.append((1, -summary_score, item))
        elif body_score:
            ranked.append((2, -body_score, item))

    ranked.sort(key=lambda entry: (entry[0], entry[1]))
    return [item for _, _, item in ranked]
