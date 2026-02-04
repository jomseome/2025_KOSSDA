import json
import re
from textwrap import shorten
from typing import Any, Dict, List

import streamlit as st
from markdown import markdown as md_to_html
from streamlit.components.v1 import html as components_html

from src.generated_content import list_stories, load_story
from src.styles import global_css
from src.visual_runtime import render_visual_from_registry

st.set_page_config(
    page_title="KOSSDA, ISDS - 한국사회, 시선",
    page_icon="📘",
    layout="wide",
)
st.markdown(global_css(), unsafe_allow_html=True)

CATEGORIES: List[Dict[str, str]] = [
    {"id": "all", "label": "전체"},
    {"id": "community", "label": "개인, 가족, 공동체"},
    {"id": "politics", "label": "정치와 시민사회"},
    {"id": "education", "label": "교육과 돌봄"},
    {"id": "work", "label": "일과 직업"},
    {"id": "economy", "label": "경제와 생활수준"},
    {"id": "environment", "label": "에너지와 환경"},
    {"id": "technology", "label": "기술과 정보"},
    {"id": "space", "label": "공간과 지역"},
]
CATEGORY_LABELS = {item["id"]: item["label"] for item in CATEGORIES}

DEFAULT_THUMBNAIL = "https://placehold.co/600x400/e5e7eb/1f2937?text=Data+Story"

VIZ_TOKEN_PATTERN = re.compile(r"\{\{\s*(?:viz|chart)(?:\s*:\s*([a-zA-Z0-9_-]+))?\s*\}\}", re.IGNORECASE)

STORY_PRESENTATION_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "covid19": {
        "category": "politics",
        "thumbnail": "https://placehold.co/600x400/9ca3af/1f2937?text=Policy",
        "excerpt": "코로나19 팬데믹 전후로 범죄 양상과 치안 구조가 어떤 변화와 과제를 남겼는지 요약했습니다.",
        "chartData": {
            "type": "line",
            "labels": ["2018", "2019", "2020"],
            "datasets": [
                {
                    "label": "강도",
                    "data": [112, 108, 82],
                    "borderColor": "rgba(59, 130, 246, 1)",
                    "backgroundColor": "rgba(59, 130, 246, 0.2)",
                    "tension": 0.25,
                    "fill": False,
                },
                {
                    "label": "절도",
                    "data": [315, 298, 240],
                    "borderColor": "rgba(250, 204, 21, 1)",
                    "backgroundColor": "rgba(250, 204, 21, 0.2)",
                    "tension": 0.25,
                    "fill": False,
                },
            ],
        },
    },
    "human22": {
        "category": "community",
        "thumbnail": "https://placehold.co/600x400/d1d5db/1f2937?text=Population",
        "excerpt": "초저출산과 고령화가 동시에 진행되는 한국 인구 구조의 전환점을 한눈에 볼 수 있습니다.",
        "chartData": {
            "type": "bar",
            "labels": ["1990", "2000", "2010", "2020", "2030"],
            "datasets": [
                {
                    "label": "출생아 수(만 명)",
                    "data": [65, 63, 47, 27, 23],
                    "backgroundColor": "rgba(59, 130, 246, 0.7)",
                    "borderColor": "rgba(59, 130, 246, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "65세 이상 인구 비중(%)",
                    "data": [5, 7.2, 11.5, 15.7, 25.5],
                    "backgroundColor": "rgba(16, 185, 129, 0.7)",
                    "borderColor": "rgba(16, 185, 129, 1)",
                    "borderWidth": 1,
                },
            ],
        },
    },
}


def _replace_visual_tokens(html: str, slot_order: List[str]) -> str:
    default_slot = slot_order[0] if slot_order else None

    def _repl(match: re.Match[str]) -> str:
        slot = match.group(1) or default_slot
        if slot and slot in slot_order:
            return (
                "<div class='plotly-slot my-8' "
                f"data-slot-id='{slot}'></div>"
            )
        display = slot or "chart"
        return f"<div class='viz-placeholder'>시각화 슬롯 `{display}` 이(가) 이곳에 렌더링됩니다.</div>"

    return VIZ_TOKEN_PATTERN.sub(_repl, html)


def _story_to_html(markdown_text: str, fmt: str, slot_order: List[str]) -> str:
    if not markdown_text:
        return "<p>콘텐츠를 준비 중입니다.</p>"
    if (fmt or "").lower() == "html":
        html = markdown_text
    else:
        html = md_to_html(markdown_text, extensions=["tables", "fenced_code"])
    html = _replace_visual_tokens(html, slot_order)
    return html.replace("</script>", "<\\/script>")


def _story_excerpt(raw_content: str, fallback: str = "") -> str:
    if not raw_content:
        return fallback
    text = re.sub(r"<[^>]+>", " ", raw_content)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return fallback
    return shorten(text, width=120, placeholder="…")


def _build_visual_slots(story_slug: str, story: Dict[str, Any]) -> List[Dict[str, Any]]:
    visuals = story.get("visuals") or {}
    slots: List[Dict[str, Any]] = []
    if not isinstance(visuals, dict):
        return slots
    for slot_id, payload in visuals.items():
        renderer = ""
        title = ""
        caption = ""
        if isinstance(payload, dict):
            renderer = payload.get("renderer") or ""
            title = payload.get("title") or ""
            caption = payload.get("caption") or ""
        slot_id = slot_id if isinstance(slot_id, str) else str(slot_id)
        if not renderer:
            continue
        fig, error = render_visual_from_registry(renderer, story_slug, slot_id)
        if error or fig is None:
            continue
        slots.append(
            {
                "slotId": slot_id,
                "title": title,
                "caption": caption,
                "figure": fig.to_plotly_json(),
            }
        )
    return slots


def _build_story_payloads() -> List[Dict[str, Any]]:
    stories = list_stories()
    payloads: List[Dict[str, Any]] = []
    for slug, title in stories.items():
        story = load_story(slug) or {}
        overrides = STORY_PRESENTATION_OVERRIDES.get(slug, {})
        category_id = overrides.get("category", "community")
        visual_slots = _build_visual_slots(slug, story)
        html = _story_to_html(
            story.get("markdown", ""),
            story.get("format", "markdown"),
            [slot["slotId"] for slot in visual_slots],
        )
        excerpt = overrides.get("excerpt") or _story_excerpt(story.get("markdown", ""))
        payloads.append(
            {
                "slug": slug,
                "title": title,
                "categoryId": category_id,
                "categoryLabel": CATEGORY_LABELS.get(category_id, "데이터 스토리"),
                "thumbnail": overrides.get("thumbnail", DEFAULT_THUMBNAIL),
                "excerpt": excerpt or "데이터 스토리 콘텐츠를 확인해보세요.",
                "html": html,
                "source": story.get("pdf_source") or "",
                "updatedAt": story.get("updated_at") or "",
                "chartData": overrides.get("chartData"),
                "plotlySlots": visual_slots,
            }
        )
    return payloads


APP_DATA = {
    "hero": {
        "tagline": "KOSSDA, ISDS",
        "title": "2025 [한국사회, 시선]",
        "subtitle": "데이터 스토리와 시각화를 통해 한국사회의 주요 이슈를 탐험합니다.",
        "cta": "보고서 살펴보기",
    },
    "categories": CATEGORIES,
    "stories": _build_story_payloads(),
    "years": [
        {"label": "2025 한국사회, 시선", "active": True},
        {"label": "2026 한국사회, 시선", "active": False},
        {"label": "2027 한국사회, 시선", "active": False},
    ],
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KOSSDA, ISDS - 한국사회, 시선</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        body { font-family: 'Inter', 'Noto Sans KR', sans-serif; }
        .content-item { transition: opacity 0.2s ease; }
        .content-item.hidden { opacity: 0.2; pointer-events: none; }
        .viz-placeholder {
            background: #f8fafc;
            border: 1px dashed #94a3b8;
            border-radius: 12px;
            padding: 1rem;
            margin: 1.5rem 0;
            font-size: 0.95rem;
            color: #475569;
            text-align: center;
        }
        .plotly-slot {
            margin: 2rem 0;
        }
        .detail-meta {
            font-size: 0.85rem;
            color: #475569;
        }
    </style>
</head>
<body class="bg-white">
    <div id="landing-page" class="fixed inset-0 bg-[#1e3a8a] flex flex-col justify-center items-center z-50">
        <div class="text-center text-white space-y-1">
            <p class="text-2xl font-medium" id="hero-tagline"></p>
            <h1 class="text-3xl md:text-4xl font-bold" id="hero-title"></h1>
        </div>
        <button id="enter-button" class="mt-12 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-10 rounded-full transition-colors duration-300">
            보고서 살펴보기
        </button>
    </div>

    <div id="main-page" class="hidden">
        <header class="bg-[#1e3a8a] text-white p-4 shadow-md">
            <h1 id="logo-main" class="text-xl font-bold cursor-pointer">KOSSDA, ISDS [한국사회, 시선]</h1>
        </header>

        <main class="container mx-auto p-4 md:p-8">
            <h2 class="text-2xl font-bold text-center mb-6" id="hero-subtitle"></h2>
            <div class="relative mb-8">
                <button id="scroll-left" class="absolute left-0 top-1/2 -translate-y-1/2 bg-white rounded-full shadow-md w-8 h-8 flex items-center justify-center z-10 opacity-75 hover:opacity-100 transition-opacity">
                    <i class="fas fa-chevron-left text-gray-600"></i>
                </button>
                <div id="category-nav" class="flex items-center space-x-2 overflow-x-auto no-scrollbar scroll-smooth px-10">
                </div>
                <button id="scroll-right" class="absolute right-0 top-1/2 -translate-y-1/2 bg-white rounded-full shadow-md w-8 h-8 flex items-center justify-center z-10 opacity-75 hover:opacity-100 transition-opacity">
                    <i class="fas fa-chevron-right text-gray-600"></i>
                </button>
            </div>
            <div class="flex flex-col md:flex-row gap-8">
                <div id="content-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 flex-grow"></div>
                <aside class="w-full md:w-64 flex-shrink-0">
                    <div class="space-y-2" id="year-links"></div>
                </aside>
            </div>
        </main>
    </div>

    <div id="detail-page" class="hidden">
        <header class="bg-[#1e3a8a] text-white p-4 shadow-md flex justify-between items-center">
            <h1 id="logo-detail" class="text-xl font-bold cursor-pointer">KOSSDA, ISDS [한국사회, 시선]</h1>
            <button id="back-to-main" class="text-white hover:text-gray-200">
                <i class="fas fa-arrow-left mr-2"></i> 목록으로
            </button>
        </header>
        <div class="container mx-auto p-4 md:p-8">
            <div class="max-w-4xl mx-auto bg-white" id="detail-content-wrapper"></div>
        </div>
    </div>

    <script>
        const APP_DATA = __APP_DATA__;
        document.addEventListener('DOMContentLoaded', () => {
            const landingPage = document.getElementById('landing-page');
            const mainPage = document.getElementById('main-page');
            const detailPage = document.getElementById('detail-page');
            const enterButton = document.getElementById('enter-button');
            const backButton = document.getElementById('back-to-main');
            const logoMain = document.getElementById('logo-main');
            const logoDetail = document.getElementById('logo-detail');
            const categoryNav = document.getElementById('category-nav');
            const scrollLeftBtn = document.getElementById('scroll-left');
            const scrollRightBtn = document.getElementById('scroll-right');
            const contentGrid = document.getElementById('content-grid');
            const detailContentWrapper = document.getElementById('detail-content-wrapper');
            const yearLinks = document.getElementById('year-links');
            let activeCategory = 'all';
            let activeChart = null;

            const hero = APP_DATA.hero || {};
            document.getElementById('hero-tagline').textContent = hero.tagline || 'KOSSDA, ISDS';
            document.getElementById('hero-title').textContent = hero.title || '한국사회, 시선';
            document.getElementById('hero-subtitle').textContent = hero.subtitle || '';
            enterButton.textContent = hero.cta || '보고서 살펴보기';

            APP_DATA.years.forEach((item) => {
                const link = document.createElement('a');
                link.href = '#';
                link.textContent = item.label;
                link.className = item.active
                    ? 'block border border-blue-600 bg-blue-100 text-blue-800 text-center font-semibold p-3 rounded-lg'
                    : 'block border border-gray-300 text-gray-600 text-center p-3 rounded-lg hover:bg-gray-100 transition-colors';
                yearLinks.appendChild(link);
            });

            function showPage(page) {
                landingPage.classList.add('hidden');
                mainPage.classList.add('hidden');
                detailPage.classList.add('hidden');
                page.classList.remove('hidden');
                window.scrollTo(0, 0);
            }

            enterButton.addEventListener('click', () => showPage(mainPage));
            backButton.addEventListener('click', () => showPage(mainPage));
            logoMain.addEventListener('click', () => showPage(landingPage));
            logoDetail.addEventListener('click', () => showPage(landingPage));

            function renderCategories() {
                APP_DATA.categories.forEach((cat, index) => {
                    const btn = document.createElement('button');
                    btn.className = 'category-btn bg-gray-200 text-gray-800 px-6 py-2 rounded-lg whitespace-nowrap flex-shrink-0 transition-colors duration-200';
                    btn.textContent = cat.label;
                    btn.dataset.category = cat.id;
                    btn.addEventListener('click', () => {
                        activeCategory = cat.id;
                        document.querySelectorAll('.category-btn').forEach((button) => {
                            button.classList.remove('bg-blue-600', 'text-white');
                            button.classList.add('bg-gray-200', 'text-gray-800');
                        });
                        btn.classList.remove('bg-gray-200', 'text-gray-800');
                        btn.classList.add('bg-blue-600', 'text-white');
                        renderCards();
                    });
                    categoryNav.appendChild(btn);
                    if (index === 0) {
                        btn.click();
                    }
                });
            }

            function attachScrollButtons() {
                scrollLeftBtn.addEventListener('click', () => {
                    categoryNav.scrollBy({ left: -200, behavior: 'smooth' });
                });
                scrollRightBtn.addEventListener('click', () => {
                    categoryNav.scrollBy({ left: 200, behavior: 'smooth' });
                });
            }

            function renderCards() {
                contentGrid.innerHTML = '';
                const stories = APP_DATA.stories.filter((story) => {
                    return activeCategory === 'all' || story.categoryId === activeCategory;
                });
                if (!stories.length) {
                    const empty = document.createElement('div');
                    empty.className = 'col-span-full text-center text-gray-500 py-20';
                    empty.textContent = '선택한 카테고리에 해당하는 콘텐츠가 없습니다.';
                    contentGrid.appendChild(empty);
                    return;
                }
                stories.forEach((story) => {
                    const card = document.createElement('div');
                    card.className = 'content-item cursor-pointer group';
                    card.dataset.slug = story.slug;
                    card.innerHTML = `
                        <div class="bg-white rounded-lg shadow-md overflow-hidden transform group-hover:-translate-y-1 transition-transform duration-300 h-full flex flex-col">
                            <div class="bg-[#1e3a8a] text-white text-sm px-3 py-1">${story.categoryLabel}</div>
                            <img src="${story.thumbnail}" alt="${story.title}" class="w-full h-48 object-cover">
                            <div class="p-4 flex flex-col flex-grow">
                                <h3 class="font-bold mb-2">${story.title}</h3>
                                <p class="text-sm text-gray-600 flex-grow">${story.excerpt}</p>
                                <span class="text-xs text-gray-400 mt-4">${story.updatedAt ? '업데이트: ' + story.updatedAt.slice(0, 10) : ''}</span>
                            </div>
                        </div>
                    `;
                    card.addEventListener('click', () => renderDetail(story.slug));
                    contentGrid.appendChild(card);
                });
            }

            function renderPlotlySlots(story) {
                if (!story.plotlySlots || !story.plotlySlots.length || typeof Plotly === 'undefined') {
                    return;
                }
                story.plotlySlots.forEach((slot, index) => {
                    const slotSelector = `.plotly-slot[data-slot-id="${slot.slotId}"]`;
                    let slotRoot = detailContentWrapper.querySelector(slotSelector);
                    if (!slotRoot) {
                        slotRoot = document.createElement('div');
                        slotRoot.className = 'plotly-slot px-6 pb-8';
                        detailContentWrapper.appendChild(slotRoot);
                    } else {
                        slotRoot.classList.add('px-6', 'pb-8');
                    }
                    const chartId = `plotly-slot-${story.slug}-${index}`;
                    slotRoot.innerHTML = `
                        ${slot.title ? `<h3 class="text-xl font-semibold mb-3">${slot.title}</h3>` : ''}
                        <div id="${chartId}" class="w-full"></div>
                        ${slot.caption ? `<p class="text-sm text-gray-500 mt-2">${slot.caption}</p>` : ''}
                    `;
                    Plotly.newPlot(chartId, slot.figure.data || [], slot.figure.layout || {}, {
                        responsive: true,
                        displayModeBar: false
                    });
                });
            }

            function renderDetail(slug) {
                const story = APP_DATA.stories.find((item) => item.slug === slug);
                if (!story) {
                    return;
                }
                if (activeChart) {
                    activeChart.destroy();
                    activeChart = null;
                }
                detailContentWrapper.innerHTML = `
                    <div class="border-b pb-4 mb-6 p-6">
                        <p class="text-sm text-blue-700 font-semibold">${story.categoryLabel}</p>
                        <h2 class="text-3xl font-bold mt-2">${story.title}</h2>
                        ${story.source ? `<p class="detail-meta mt-2">데이터/출처: ${story.source}</p>` : ''}
                    </div>
                    <div class="prose lg:prose-lg max-w-none px-6 pb-12">${story.html}</div>
                `;
                if (story.chartData) {
                    const chartBlock = document.createElement('div');
                    chartBlock.className = 'px-6 pb-10';
                    const canvas = document.createElement('canvas');
                    canvas.id = `detail-chart-${story.slug}`;
                    chartBlock.appendChild(canvas);
                    detailContentWrapper.appendChild(chartBlock);
                    const ctx = canvas.getContext('2d');
                    activeChart = new Chart(ctx, {
                        type: story.chartData.type || 'bar',
                        data: {
                            labels: story.chartData.labels || [],
                            datasets: story.chartData.datasets || [],
                        },
                        options: story.chartData.options || {
                            responsive: true,
                            scales: { y: { beginAtZero: true } },
                        },
                    });
                }
                renderPlotlySlots(story);
                showPage(detailPage);
            }

            renderCategories();
            attachScrollButtons();
            renderCards();
        });
    </script>
</body>
</html>
"""


def _render_visual_shell() -> None:
    payload = json.dumps(APP_DATA, ensure_ascii=False)
    components_html(
        HTML_TEMPLATE.replace("__APP_DATA__", payload),
        height=1800,
        scrolling=True,
    )


_render_visual_shell()
