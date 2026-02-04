from __future__ import annotations

import random
import re
from datetime import datetime
from pathlib import Path
from textwrap import shorten
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from .chart_builder import build_chart
from .generated_content import list_stories, load_story
from .story_render import render_story_content
from .visual_runtime import render_interactive_panel, render_visual_from_registry
from .workspace_data import DATA_DIR

PLACEHOLDER_TOKENS = (
    "{{viz}}",
    "{{ chart }}",
    "{{chart}}",
    "&#123;&#123;chart&#125;&#125;",
    "&lbrace;&lbrace;chart&rbrace;&rbrace;",
)

TOPICS: List[Dict[str, Any]] = [
    {
        "id": "economy",
        "label": "경제",
        "color": "#1f77b4",
        "description": "성장률·고용·생산성을 묶어보는 경제 진단 허브",
        "emoji": "💹",
    },
    {
        "id": "welfare",
        "label": "복지",
        "color": "#2ca02c",
        "description": "불평등과 사회지출의 변화를 함께 점검합니다.",
        "emoji": "🤝",
    },
    {
        "id": "education",
        "label": "교육",
        "color": "#ff7f0e",
        "description": "학력·역량·교육격차를 데이터로 추적합니다.",
        "emoji": "🎓",
    },
    {
        "id": "environment",
        "label": "환경",
        "color": "#17becf",
        "description": "탄소·대기질·에너지 구조를 시계열로 살펴봅니다.",
        "emoji": "🌏",
    },
    {
        "id": "gender",
        "label": "젠더",
        "color": "#9467bd",
        "description": "임금격차와 돌봄노동, 젠더 기반 지표를 묶었습니다.",
        "emoji": "⚧️",
    },
    {
        "id": "politics",
        "label": "정치",
        "color": "#8c564b",
        "description": "참여·신뢰·정당정치를 데이터로 읽어봅니다.",
        "emoji": "🗳️",
    },
    {
        "id": "qol",
        "label": "삶의 질",
        "color": "#e377c2",
        "description": "행복·여가·정서 지표를 통합한 삶의 질 탐색.",
        "emoji": "🙂",
    },
]

YEARS = list(range(2012, 2026))
REGIONS = [
    "전국",
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
]

INDICATORS: Dict[str, List[Dict[str, Any]]] = {
    "economy": [
        {"id": "gdp", "label": "1인당 GDP", "unit": "$", "seed": 11},
        {"id": "unemp", "label": "실업률", "unit": "%", "seed": 12},
        {"id": "prod", "label": "노동생산성", "unit": "지수", "seed": 13},
    ],
    "welfare": [
        {"id": "poverty", "label": "상대적 빈곤율", "unit": "%", "seed": 21},
        {"id": "spend", "label": "사회지출", "unit": "%GDP", "seed": 22},
    ],
    "education": [
        {"id": "tertiary", "label": "고등교육 이수율", "unit": "%", "seed": 31},
        {"id": "pisa", "label": "PISA 점수", "unit": "점", "seed": 32},
    ],
    "environment": [
        {"id": "pm25", "label": "PM2.5", "unit": "µg/m³", "seed": 41},
        {"id": "co2", "label": "1인당 CO₂", "unit": "t", "seed": 42},
    ],
    "gender": [
        {"id": "paygap", "label": "성별 임금격차", "unit": "%", "seed": 51},
        {"id": "maternity", "label": "출산휴가 사용률", "unit": "%", "seed": 52},
    ],
    "politics": [
        {"id": "turnout", "label": "투표율", "unit": "%", "seed": 61},
        {"id": "trust", "label": "정부 신뢰", "unit": "%", "seed": 62},
    ],
    "qol": [
        {"id": "happiness", "label": "행복지수", "unit": "점", "seed": 71},
        {"id": "leisure", "label": "여가시간", "unit": "시간", "seed": 72},
    ],
}

TIMELINE_EVENTS = [
    {"year": 2015, "label": "정책 A 시행"},
    {"year": 2019, "label": "지표 기준 개정"},
    {"year": 2023, "label": "국가전략 발표"},
]

STORY_CHART_WIDTH = 880
STORY_CHART_HEIGHT = 420


def _series(seed: int, scale: int = 100) -> List[Dict[str, float]]:
    rng = random.Random(seed)
    return [{"year": year, "value": round(rng.random() * scale, 2)} for year in YEARS]


def _build_mock_db() -> Dict[str, Dict[str, Dict[str, List[Dict[str, float]]]]]:
    payload: Dict[str, Dict[str, Dict[str, List[Dict[str, float]]]]] = {}
    for topic_id, indicators in INDICATORS.items():
        topic_payload: Dict[str, Dict[str, List[Dict[str, float]]]] = {}
        for idx, ind in enumerate(indicators):
            indicator_payload: Dict[str, List[Dict[str, float]]] = {}
            for region_index, region in enumerate(REGIONS):
                indicator_payload[region] = _series(ind["seed"] + region_index + idx, 100)
            topic_payload[ind["id"]] = indicator_payload
        payload[topic_id] = topic_payload
    return payload


MOCK_DB = _build_mock_db()

EDUCATION_LAB_DATASETS: Dict[str, Dict[str, Any]] = {
    "education-care-realignment": {
        "title": "미래사회의 문턱에서 한국의 교육 훈련 돌봄 체계는 어떻게 재정렬되고 있는가",
        "path": DATA_DIR
        / "excel_data"
        / "(임시본)교육훈련 및 돌봄분야 데이터 모음.xlsx",
    }
}


def _education_lab_datasets() -> Dict[str, Dict[str, Any]]:
    datasets: Dict[str, Dict[str, Any]] = {}
    for slug, meta in EDUCATION_LAB_DATASETS.items():
        path = meta.get("path")
        if not isinstance(path, Path) or not path.exists():
            continue
        payload = load_story(slug) or {}
        title = payload.get("title") or meta.get("title") or slug
        datasets[slug] = {"slug": slug, "title": title, "path": path}
    return datasets


@st.cache_data(show_spinner=False)
def _list_excel_sheets(path_value: str) -> List[str]:
    excel = pd.ExcelFile(path_value)
    return excel.sheet_names


@st.cache_data(show_spinner=False)
def _load_excel_sheet(path_value: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(path_value, sheet_name=sheet_name)


from .visual_runtime import render_visual_from_registry, render_interactive_panel


def _build_visual_entries(story_slug: str, story: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    entries: Dict[str, Dict[str, Any]] = {}
    visuals = story.get("visuals") or {}
    if isinstance(visuals, dict):
        for idx, (slot_id, payload) in enumerate(visuals.items(), start=1):
            key = slot_id if isinstance(slot_id, str) else f"slot-{idx}"
            renderer = None
            title = None
            caption = None
            if isinstance(payload, dict):
                renderer = payload.get("renderer")
                title = payload.get("title")
                caption = payload.get("caption")
            entries[key] = {
                "renderer": renderer if isinstance(renderer, str) else "",
                "title": title,
                "caption": caption,
            }
    return entries


def _get_query_param(name: str) -> Optional[str]:
    try:
        value = st.query_params.get(name)
    except Exception:  # pragma: no cover - legacy API fallback
        value = st.experimental_get_query_params().get(name)
    if isinstance(value, list):
        return value[0] if value else None
    if value == "":
        return None
    return value


def _set_query_param(**params) -> None:
    if not params:
        return
    try:
        for key, value in params.items():
            if value is None:
                if key in st.query_params:
                    del st.query_params[key]
            else:
                st.query_params[key] = value
    except Exception:  # pragma: no cover - legacy API fallback
        current = dict(st.experimental_get_query_params())
        for key, value in params.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value
        st.experimental_set_query_params(**current)


def _queue_navigation(page: str, *, slug: Optional[str] = None, topic_id: Optional[str] = None) -> None:
    st.session_state["pending_nav"] = {
        "page": page,
        "slug": slug,
        "topic_id": topic_id,
    }


def _suggest_topic_story_map(stories: Dict[str, str]) -> Dict[str, Optional[str]]:
    mapping: Dict[str, Optional[str]] = {topic["id"]: None for topic in TOPICS}
    available = list(stories.keys())

    # 1) 직접 아이디가 매칭되는 경우 우선 연결
    for topic in TOPICS:
        if topic["id"] in stories:
            mapping[topic["id"]] = topic["id"]
            if topic["id"] in available:
                available.remove(topic["id"])

    # 2) 남은 스토리를 순서대로 매핑
    for topic in TOPICS:
        if mapping[topic["id"]] is None and available:
            mapping[topic["id"]] = available.pop(0)

    return mapping


def _reverse_topic_story_map(topic_story_map: Dict[str, Optional[str]]) -> Dict[str, str]:
    return {slug: topic_id for topic_id, slug in topic_story_map.items() if slug}


def _topic_label(slug: str, story_to_topic: Dict[str, str]) -> str:
    topic_id = story_to_topic.get(slug)
    if not topic_id:
        return "데이터 스토리"
    topic_meta = next((topic for topic in TOPICS if topic["id"] == topic_id), None)
    return topic_meta["label"] if topic_meta else "데이터 스토리"


def _extract_excerpt(story: Dict[str, Any], default: str = "") -> str:
    text = story.get("markdown") or ""
    if not text:
        return default
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return shorten(text, width=120, placeholder="…") if text else default


def _format_updated_at(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return value
    return timestamp.strftime("%Y-%m-%d %H:%M")


def _auto_inject_placeholder(content: str) -> str:
    normalized = content
    if _has_chart_placeholder(normalized):
        return normalized
    lower = normalized.lower()
    for marker in ("</h2>", "</h3>", "</h4>", "</p>", "</section>"):
        idx = lower.find(marker)
        if idx != -1:
            insert_at = idx + len(marker)
            return (
                normalized[:insert_at]
                + f"\n\n{PLACEHOLDER_TOKENS[0]}\n\n"
                + normalized[insert_at:]
            )
    if "\n\n" in normalized:
        head, tail = normalized.split("\n\n", 1)
        return f"{head}\n\n{PLACEHOLDER_TOKENS[0]}\n\n{tail}"
    return normalized + f"\n\n{PLACEHOLDER_TOKENS[0]}"


PLACEHOLDER_SEARCH = re.compile(
    r"(\{\{\s*(chart|viz))|(&#123;&#123;\s*(chart|viz))|(&lbrace;&lbrace;\s*(chart|viz))",
    re.IGNORECASE,
)


def _has_chart_placeholder(content: str) -> bool:
    return bool(PLACEHOLDER_SEARCH.search(content))


def _render_centered_chart(
    fig: Any,
    *,
    key: Optional[str],
    caption: Optional[str] = None,
    default_height: int = STORY_CHART_HEIGHT,
) -> None:
    fig.update_layout(
        width=STORY_CHART_WIDTH,
        height=fig.layout.height or default_height,
        margin=dict(l=40, r=24, t=48, b=40),
    )
    left, center, right = st.columns([1.5, 8, 1.5], gap="small")
    with center:
        st.plotly_chart(
            fig,
            use_container_width=False,
            key=key,
            config={"displayModeBar": False, "responsive": True},
        )
        if caption:
            st.caption(caption)


def _render_centered_markdown(markdown_text: str) -> None:
    left, center, right = st.columns([1.5, 8, 1.5], gap="small")
    with center:
        st.markdown(markdown_text, unsafe_allow_html=True)


def _render_story_chart(
    fig: Any,
    chart_meta: Optional[Dict[str, Any]],
    chart_key: Optional[str],
) -> None:
    fig.update_layout(
        width=STORY_CHART_WIDTH,
        height=fig.layout.height or STORY_CHART_HEIGHT,
        margin=dict(l=40, r=40, t=32, b=32),
    )
    caption = None
    if isinstance(chart_meta, dict):
        workbook_label = chart_meta.get("workbook")
        sheet_label = chart_meta.get("sheet")
        if workbook_label or sheet_label:
            caption = f"데이터 출처: `{workbook_label}` · 시트 `{sheet_label}`"
    left, center, right = st.columns([1.5, 8, 1.5], gap="small")
    with center:
        st.markdown("<div class='story-figure'>", unsafe_allow_html=True)
        st.plotly_chart(
            fig,
            use_container_width=False,
            key=chart_key,
            config={"displayModeBar": False, "responsive": True},
        )
        if caption:
            st.markdown(f"<p class='story-caption'>{caption}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_story_block(
    story: Dict[str, Any],
    story_slug: str,
    visual_entries: Dict[str, Dict[str, Any]],
) -> None:
    title = story.get("title") or story_slug
    pdf_source = story.get("pdf_source")
    updated_at = _format_updated_at(story.get("updated_at"))

    st.markdown(f"### {title}")
    if pdf_source:
        st.caption(f"텍스트 출처: `{pdf_source}`")
    if updated_at:
        st.caption(f"최종 업데이트: {updated_at}")

    markdown_text = story.get("markdown") or ""
    if visual_entries and not _has_chart_placeholder(markdown_text):
        markdown_text = _auto_inject_placeholder(markdown_text)

    default_slot = next(iter(visual_entries.keys()), None)

    render_counts: Dict[str, int] = {}

    def _chart_renderer(chart_id: Optional[str]) -> Optional[bool]:
        target_id = chart_id or default_slot
        if not target_id:
            st.info("시각화 슬롯이 설정되지 않았습니다.")
            return False
        entry = visual_entries.get(target_id)
        if not entry:
            st.info(f"시각화 슬롯 `{target_id}`을(를) 찾을 수 없습니다.")
            return False
        renderer_name = (entry.get("renderer") or "").strip()
        if not renderer_name:
            st.info(f"`{target_id}` 슬롯에 렌더러 이름이 지정되지 않았습니다.")
            return False
        fig_obj, error = render_visual_from_registry(renderer_name, story_slug, target_id)
        if error:
            st.warning(f"`{target_id}` 렌더러 실행 오류: {error}")
            return False
        chart_title = entry.get("title")
        if chart_title:
            _render_centered_markdown(f"#### {chart_title}")
        render_counts[target_id] = render_counts.get(target_id, 0) + 1
        fig_obj.update_layout(width=STORY_CHART_WIDTH, height=fig_obj.layout.height or STORY_CHART_HEIGHT)
        unique_key = f"story_chart_{story_slug}_{target_id}_{render_counts[target_id]}"
        _render_story_chart(fig_obj, None, unique_key)
        caption_text = entry.get("caption")
        if caption_text:
            _render_centered_markdown(f"<p class='story-caption'>{caption_text}</p>")
        return True

    content_format = story.get("format", "markdown")
    chart_renderer = _chart_renderer if visual_entries else None

    if markdown_text:
        render_story_content(
            markdown_text,
            content_format=content_format,
            chart_renderer=chart_renderer,
        )
    else:
        st.info("본문 텍스트가 제공되지 않았습니다.")
        if chart_renderer:
            chart_renderer(default_slot)

    if not visual_entries:
        st.info("시각화 슬롯이 아직 설정되지 않았습니다.")

    render_interactive_panel(story_slug)


def _chunk(items: List[Any], size: int) -> List[List[Any]]:
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


def _render_home_page(
    stories: Dict[str, str],
    story_payloads: Dict[str, Dict[str, Any]],
    topic_story_map: Dict[str, Optional[str]],
    story_to_topic: Dict[str, str],
) -> None:
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-card__text">
            <span class="hero-chip">한국 사회, 시선</span>
            <h1>이슈별로 읽는 7개 테마 허브</h1>
            <p>경제·복지·교육·환경·젠더·정치·삶의 질까지 핵심 지표와 데이터 스토리를 하나의 리듬으로 읽습니다.</p>
            <p class="hero-sub">데이터 기반 탐색 · 비교 · 타임라인까지 한 곳에서.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 오늘의 하이라이트")
    highlight_topics = TOPICS[:4]
    columns = st.columns(len(highlight_topics))
    for column, topic in zip(columns, highlight_topics):
        with column:
            seed = sum(ord(ch) for ch in topic["id"])
            trend_data = _series(seed & 0xFFFF)
            trend_df = pd.DataFrame(trend_data)
            fig = px.area(trend_df, x="year", y="value", title=None)
            fig.update_layout(
                height=180,
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title=None,
                yaxis_title=None,
            )
            fig.update_traces(line=dict(color=topic["color"]), fillcolor=topic["color"])

            st.markdown(
                f"""
                <div class="mini-card">
                  <div class="mini-card__meta">{topic['emoji']} {topic['label']}</div>
                  <div class="mini-card__title">{topic['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"home_trend_{topic['id']}",
            )

    st.markdown("#### 최신 데이터 스토리")
    story_slugs = list(stories.keys())[:3]
    if not story_slugs:
        st.info("게시된 데이터 스토리가 아직 없습니다.")
        return

    cols = st.columns(len(story_slugs))
    for col, slug in zip(cols, story_slugs):
        with col:
            payload = story_payloads.get(slug, {})
            title = payload.get("title") or stories[slug]
            excerpt = _extract_excerpt(payload, "스토리 내용을 준비 중입니다.")
            updated = _format_updated_at(payload.get("updated_at"))
            st.markdown(
                f"""
                <div class="story-card">
                  <span class="story-card__topic">{_topic_label(slug, story_to_topic)}</span>
                  <h3>{title}</h3>
                  <p>{excerpt}</p>
                  {f"<div class='story-card__meta'>업데이트 {updated}</div>" if updated else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("스토리 열기", key=f"home_open_{slug}", use_container_width=True):
                _queue_navigation(
                    "topics",
                    slug=slug,
                    topic_id=story_to_topic.get(slug),
                )
                st.rerun()


def _render_topic_grid(
    stories: Dict[str, str],
    story_payloads: Dict[str, Dict[str, Any]],
    topic_story_map: Dict[str, Optional[str]],
) -> None:
    st.markdown("### 주제별 리포트")
    st.caption("현황 요약 · 데이터 스토리 · 국제 비교 · 정책 타임라인")

    for row in _chunk(TOPICS, 3):
        cols = st.columns(3, gap="large")
        for topic, col in zip(row, cols):
            with col:
                slug = topic_story_map.get(topic["id"])
                payload = story_payloads.get(slug or "", {})
                title = payload.get("title") if payload else None
                excerpt = _extract_excerpt(payload, "데이터 스토리가 연결되면 자동으로 미리보기로 표시됩니다.")
                st.markdown(
                    f"""
                    <div class="topic-card">
                      <div class="topic-card__icon" style="background:{topic['color']};">{topic['emoji']}</div>
                      <div class="topic-card__body">
                        <h3>{topic['label']}</h3>
                        <p>{topic['description']}</p>
                        <div class="topic-card__footer">
                          <span>{'연결된 스토리: ' + title if title else '연결된 스토리가 없습니다.'}</span>
                        </div>
                      </div>
                      <div class="topic-card__preview">{excerpt}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("자세히 보기", key=f"topic_open_{topic['id']}", use_container_width=True):
                    _queue_navigation(
                        "topics",
                        slug=slug,
                        topic_id=topic["id"],
                    )
                    st.rerun()


def _render_topic_detail(
    topic_id: str,
    stories: Dict[str, str],
    story_payloads: Dict[str, Dict[str, Any]],
    topic_story_map: Dict[str, Optional[str]],
    story_visual_map: Dict[str, Dict[str, Dict[str, Any]]],
) -> None:
    topic_meta = next((item for item in TOPICS if item["id"] == topic_id), None)
    if topic_meta is None:
        st.session_state["opened_topic"] = None
        return

    if st.button("← 목록으로 돌아가기", key="topic_back"):
        st.session_state["opened_topic"] = None
        _set_query_param(story=None)
        st.rerun()

    st.markdown(f"## {topic_meta['emoji']} {topic_meta['label']}")
    st.caption(topic_meta["description"])

    indicator_key = f"{topic_id}_indicator"
    region_a_key = f"{topic_id}_region_a"
    region_b_key = f"{topic_id}_region_b"

    indicators = INDICATORS[topic_id]
    if indicator_key not in st.session_state:
        st.session_state[indicator_key] = indicators[0]["id"]
    if region_a_key not in st.session_state:
        st.session_state[region_a_key] = "전국"
    if region_b_key not in st.session_state:
        st.session_state[region_b_key] = "서울"

    cols = st.columns([1.2, 1, 1, 1])
    with cols[0]:
        st.selectbox(
            "지표",
            options=[indicator["id"] for indicator in indicators],
            key=indicator_key,
            format_func=lambda value: next(ind["label"] for ind in indicators if ind["id"] == value),
        )
    with cols[1]:
        st.selectbox("지역 A", options=REGIONS, key=region_a_key)
    with cols[2]:
        st.selectbox("지역 B", options=REGIONS, key=region_b_key)
    with cols[3]:
        selected_indicator = st.session_state[indicator_key]
        region_a = st.session_state[region_a_key]
        region_b = st.session_state[region_b_key]

        df_a = pd.DataFrame(MOCK_DB[topic_id][selected_indicator][region_a])
        df_b = pd.DataFrame(MOCK_DB[topic_id][selected_indicator][region_b])
        combined = pd.DataFrame(
            {
                "year": YEARS,
                region_a: df_a["value"].values,
                region_b: df_b["value"].values,
            }
        )
        csv_bytes = combined.to_csv(index=False).encode("utf-8")
        st.download_button(
            "CSV 다운로드",
            data=csv_bytes,
            file_name=f"{topic_id}_{selected_indicator}.csv",
            mime="text/csv",
        )

    selected_indicator = st.session_state[indicator_key]
    region_a = st.session_state[region_a_key]
    region_b = st.session_state[region_b_key]
    indicator_meta = next(ind for ind in indicators if ind["id"] == selected_indicator)
    df_a = pd.DataFrame(MOCK_DB[topic_id][selected_indicator][region_a])
    df_b = pd.DataFrame(MOCK_DB[topic_id][selected_indicator][region_b])
    combined = pd.DataFrame(
        {
            "year": YEARS,
            region_a: df_a["value"].values,
            region_b: df_b["value"].values,
        }
    )

    summary_fig = px.line(
        combined,
        x="year",
        y=[region_a, region_b],
        markers=True,
        color_discrete_sequence=[topic_meta["color"], "#1f2937"],
    )
    summary_fig.update_layout(
        height=480,
        legend_title=None,
        margin=dict(l=16, r=16, t=32, b=16),
        xaxis_title="연도",
        yaxis_title=f"{indicator_meta['label']} ({indicator_meta['unit']})",
    )

    mini = pd.DataFrame(_series(indicator_meta["seed"], 100))
    mini_fig = px.area(mini, x="year", y="value", color_discrete_sequence=[topic_meta["color"]])
    mini_fig.update_layout(
        height=220,
        showlegend=False,
        margin=dict(l=16, r=16, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
    )

    compare_df = pd.DataFrame(
        {
            "year": YEARS,
            "한국": df_a["value"],
            "OECD 평균": df_b["value"] * 0.9 + 5,
        }
    )
    compare_fig = px.line(compare_df, x="year", y=["한국", "OECD 평균"], markers=True)
    compare_fig.update_layout(
        height=420,
        margin=dict(l=16, r=16, t=32, b=16),
        legend_title=None,
    )

    story_options: List[Tuple[str, str]] = []
    unique_slugs = set()
    for slug in topic_story_map.values():
        if slug and slug in story_payloads and slug not in unique_slugs:
            payload = story_payloads[slug]
            story_options.append((slug, payload.get("title") or stories.get(slug, slug)))
            unique_slugs.add(slug)

    if story_options:
        default_slug = topic_story_map.get(topic_id) or story_options[0][0]
        title_map = {slug: title for slug, title in story_options}
        if "selected_story" not in st.session_state or st.session_state["selected_story"] not in title_map:
            st.session_state["selected_story"] = default_slug
        options = list(title_map.keys())
        selected_slug = st.selectbox(
            "데이터 스토리 선택",
            options=options,
            index=options.index(st.session_state["selected_story"]),
            format_func=lambda slug: title_map.get(slug, slug),
        )
        if selected_slug != st.session_state.get("selected_story"):
            st.session_state["selected_story"] = selected_slug
        _set_query_param(story=st.session_state["selected_story"])
    else:
        st.info("연결된 데이터 스토리가 없습니다.")

    story_tab, summary_tab, compare_tab, timeline_tab = st.tabs(
        ["데이터 스토리", "현황 요약", "국제 비교", "정책 타임라인"]
    )

    with story_tab:
        slug = st.session_state.get("selected_story")
        if slug and slug in story_payloads:
            visual_entries = story_visual_map.get(slug, {})
            _render_story_block(story_payloads[slug], slug, visual_entries)
        else:
            st.info("연결된 데이터 스토리를 선택하면 내용이 표시됩니다.")

    with summary_tab:
        _render_centered_chart(summary_fig, key=f"summary_chart_{topic_id}", default_height=480)
        _render_centered_markdown("##### 키 인사이트 (데모)")
        _render_centered_chart(mini_fig, key=f"mini_chart_{topic_id}", default_height=220)

    with compare_tab:
        _render_centered_chart(compare_fig, key=f"compare_chart_{topic_id}", default_height=420)
        _render_centered_markdown("<p class='chart-note'>※ 실제 서비스에서는 OWID/OECD API 또는 정적 CSV를 연결합니다.</p>")

    with timeline_tab:
        for item in TIMELINE_EVENTS:
            st.markdown(
                f"""
                <div class="timeline-row">
                  <div class="timeline-dot"></div>
                  <div>
                    <div class="timeline-year">{item['year']}</div>
                    <div class="timeline-text">{item['label']}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_lab_page() -> None:
    st.markdown("### 데이터 랩")
    st.caption("원데이터 기반 시각화 실험실 (데모 데이터)")

    topic = st.selectbox(
        "주제",
        options=[topic["id"] for topic in TOPICS],
        format_func=lambda value: next(t["label"] for t in TOPICS if t["id"] == value),
        key="lab_topic",
    )
    if topic == "education":
        st.caption("교육 주제는 실제 스토리 데이터로 자유 시각화를 제공합니다.")
        datasets = _education_lab_datasets()
        if not datasets:
            st.warning("교육 데이터 세트를 찾을 수 없습니다.")
            return

        dataset_slugs = list(datasets.keys())
        selected_slug = st.selectbox(
            "스토리",
            options=dataset_slugs,
            format_func=lambda slug: datasets[slug]["title"],
            key="lab_edu_story",
        )
        selected_dataset = datasets[selected_slug]
        path_value = str(selected_dataset["path"])

        sheets = _list_excel_sheets(path_value)
        if not sheets:
            st.warning("선택한 스토리의 데이터 시트를 찾을 수 없습니다.")
            return

        sheet = st.selectbox("데이터 시트", options=sheets, key="lab_edu_sheet")
        df = _load_excel_sheet(path_value, sheet).copy()

        with st.expander("데이터 미리보기", expanded=False):
            st.dataframe(df.head(12), use_container_width=True)

        chart_type = st.selectbox(
            "차트 유형",
            options=["line", "bar", "scatter", "area"],
            format_func=lambda value: {
                "line": "선",
                "bar": "막대",
                "scatter": "산점도",
                "area": "영역",
            }[value],
            key="lab_edu_chart_type",
        )

        columns = list(df.columns)
        x_col = st.selectbox("X축", options=columns, key="lab_edu_x")
        y_candidates = [col for col in columns if col != x_col]
        y_default = y_candidates[:1] if y_candidates else []
        y_cols = st.multiselect("Y축", options=y_candidates, default=y_default, key="lab_edu_y")
        color_col = st.selectbox("색상 그룹(선택)", options=["없음"] + columns, key="lab_edu_color")
        coerce_numeric = st.checkbox("Y축 숫자 변환", value=True, key="lab_edu_numeric")

        if not y_cols:
            st.info("Y축을 최소 1개 선택해 주세요.")
            return
        if chart_type == "scatter" and len(y_cols) != 1:
            st.info("산점도는 Y축을 1개만 선택할 수 있습니다.")
            return

        plot_df = df.copy()
        if coerce_numeric:
            for col in y_cols:
                plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce")

        if y_cols:
            plot_df = plot_df.dropna(subset=[x_col] + y_cols)

        plot_kwargs = {
            "x": x_col,
            "color": None if color_col == "없음" else color_col,
        }

        if chart_type == "line":
            fig = px.line(plot_df, y=y_cols, markers=True, **plot_kwargs)
        elif chart_type == "bar":
            fig = px.bar(plot_df, y=y_cols, barmode="group", **plot_kwargs)
        elif chart_type == "area":
            fig = px.area(plot_df, y=y_cols, **plot_kwargs)
        else:
            fig = px.scatter(plot_df, y=y_cols[0], **plot_kwargs)

        fig.update_layout(
            height=480,
            margin=dict(l=16, r=16, t=32, b=16),
            hovermode="closest",
        )
        _render_centered_chart(
            fig,
            key=f"lab_chart_edu_{selected_slug}_{sheet}_{chart_type}",
            default_height=480,
        )
        st.caption("데이터 랩은 연구자·언론인용 빠른 탐색을 목표로 합니다.")
        return

    indicators = INDICATORS[topic]
    indicator_ids = [indicator["id"] for indicator in indicators]
    if st.session_state.get("lab_indicator") not in indicator_ids:
        st.session_state["lab_indicator"] = indicator_ids[0]
    indicator = st.selectbox(
        "지표",
        options=indicator_ids,
        format_func=lambda value: next(ind["label"] for ind in indicators if ind["id"] == value),
        key="lab_indicator",
    )
    region = st.selectbox("지역", options=REGIONS, key="lab_region")

    df = pd.DataFrame(MOCK_DB[topic][indicator][region])
    lab_fig = px.line(df, x="year", y="value", markers=True)
    lab_fig.update_layout(
        height=480,
        margin=dict(l=16, r=16, t=32, b=16),
        xaxis_title="연도",
        yaxis_title="값",
        hovermode="closest",
    )
    _render_centered_chart(
        lab_fig,
        key=f"lab_chart_{topic}_{indicator}_{region}",
        default_height=480,
    )
    st.caption("데이터 랩은 연구자·언론인용 빠른 탐색을 목표로 합니다. (데모 데이터)")


def _render_archive_page(
    stories: Dict[str, str],
    story_payloads: Dict[str, Dict[str, Any]],
    story_to_topic: Dict[str, str],
) -> None:
    st.markdown("### 인사이트 아카이브")
    st.caption("과거 리포트/블로그 모음 · 태그 검색")

    query = st.text_input("검색 (제목/본문)", key="archive_query")
    if query:
        query_lower = query.lower()
    else:
        query_lower = ""

    entries: List[Tuple[str, Dict[str, Any]]] = []
    for slug, payload in story_payloads.items():
        title = payload.get("title") or stories.get(slug, slug)
        summary = _extract_excerpt(payload, "")
        haystack = f"{title} {summary}".lower()
        if query_lower and query_lower not in haystack:
            continue
        entries.append((slug, payload))

    if not entries:
        st.info("조건에 맞는 스토리가 없습니다.")
        return

    for row in _chunk(entries, 3):
        cols = st.columns(3, gap="large")
        for (slug, payload), col in zip(row, cols):
            with col:
                title = payload.get("title") or stories.get(slug, slug)
                updated = _format_updated_at(payload.get("updated_at"))
                excerpt = _extract_excerpt(payload, "내용을 확인하려면 스토리를 엽니다.")
                tag_label = _topic_label(slug, story_to_topic)
                st.markdown(
                    f"""
                    <div class="archive-card">
                      <div class="archive-card__tag">{tag_label}</div>
                      <h3>{title}</h3>
                      <p>{excerpt}</p>
                      {f"<div class='archive-card__meta'>업데이트 {updated}</div>" if updated else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("열기", key=f"archive_open_{slug}", use_container_width=True):
                    _queue_navigation(
                        "topics",
                        slug=slug,
                        topic_id=story_to_topic.get(slug),
                    )
                    st.rerun()


def _render_about_page() -> None:
    st.markdown("### About / Team")
    st.caption("프로젝트 취지 · 데이터 출처 · 협업 제안")

    st.markdown(
        """
        <div class="about-grid">
          <div class="about-card">
            <h4>프로젝트 소개</h4>
            <p>‘한국 사회, 시선’은 7개 이슈 축으로 한국 사회의 주요 변동을 정리하고, 데이터 스토리와 시각화를 결합한 허브입니다.</p>
            <p>사회지표를 단일 페이지에서 읽고 비교하며, 정책 타임라인까지 연결하는 프로토타입을 목표로 합니다.</p>
          </div>
          <div class="about-card">
            <h4>오픈 데이터 & 오픈 소스</h4>
            <p>OWID / OECD / UN / KOSIS 등 공개 데이터셋을 연결하고, 시각화 템플릿을 점진적으로 공개할 예정입니다. 협업 제안은 언제든지 환영합니다.</p>
            <div class="about-links">
              <a href="#" class="about-link">GitHub</a>
              <a href="#" class="about-link about-link--primary">뉴스레터 구독</a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_public_view() -> None:
    stories = list_stories()
    if not stories:
        st.warning("아직 게시된 데이터 스토리가 없습니다. 관리자가 먼저 저장해야 합니다.")
        return

    story_payloads = {slug: load_story(slug) or {} for slug in stories}
    story_visual_map = {slug: _build_visual_entries(slug, payload) for slug, payload in story_payloads.items()}
    topic_story_map = _suggest_topic_story_map(stories)
    story_to_topic = _reverse_topic_story_map(topic_story_map)
    requested_slug = _get_query_param("story")

    pending_nav = st.session_state.pop("pending_nav", None)

    if "nav_radio" not in st.session_state:
        st.session_state["nav_radio"] = (
            "topics" if requested_slug and requested_slug in story_payloads else "home"
        )
    if "opened_topic" not in st.session_state:
        st.session_state["opened_topic"] = None
    if "selected_story" not in st.session_state:
        st.session_state["selected_story"] = (
            requested_slug if requested_slug in story_payloads else next(iter(story_payloads))
        )

    if requested_slug and requested_slug in story_payloads:
        st.session_state["selected_story"] = requested_slug
        st.session_state["opened_topic"] = story_to_topic.get(
            requested_slug, st.session_state.get("opened_topic")
        )

    if pending_nav:
        target_page = pending_nav.get("page", "home")
        target_slug = pending_nav.get("slug")
        target_topic = pending_nav.get("topic_id") or (
            story_to_topic.get(target_slug) if target_slug else None
        )

        st.session_state["nav_radio"] = target_page

        if target_topic:
            st.session_state["opened_topic"] = target_topic
        if target_slug and target_slug in story_payloads:
            st.session_state["selected_story"] = target_slug
            _set_query_param(story=target_slug)
        else:
            _set_query_param(story=None)

    st.markdown(
        """
        <div class="app-header">
          <div class="brand">
            <span class="brand__logo">시</span>
            <div>
              <div class="brand__name">한국 사회, 시선</div>
              <div class="brand__tagline">테마 기반 데이터 허브</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_items = [
        ("home", "메인"),
        ("topics", "주제"),
        ("lab", "데이터 랩"),
        ("archive", "인사이트 아카이브"),
        ("about", "About"),
    ]
    nav_labels = {value: label for value, label in nav_items}
    page = st.radio(
        "페이지 이동",
        options=[value for value, _ in nav_items],
        format_func=lambda value: nav_labels[value],
        key="nav_radio",
        horizontal=True,
        label_visibility="collapsed",
    )

    if page != "topics":
        st.session_state["opened_topic"] = None
        _set_query_param(story=None)

    if page == "home":
        _render_home_page(stories, story_payloads, topic_story_map, story_to_topic)
    elif page == "topics":
        opened_topic = st.session_state.get("opened_topic")
        if opened_topic:
            _render_topic_detail(opened_topic, stories, story_payloads, topic_story_map, story_visual_map)
        else:
            _render_topic_grid(stories, story_payloads, topic_story_map)
    elif page == "lab":
        _render_lab_page()
    elif page == "archive":
        _render_archive_page(stories, story_payloads, story_to_topic)
    elif page == "about":
        _render_about_page()
