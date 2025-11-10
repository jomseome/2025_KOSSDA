import html

import streamlit as st
from ..ui import top_blue_bar, category_bar, year_list
from ..content_loader import get_contents, search_contents
from ..data import CATEGORIES
from .registry import page


@page(
    "main",
    title="메인",
    description="카테고리별 개요",
)
def render(context: dict | None = None):
    context = context or {}
    top_blue_bar()
    # 가로 스크롤 가능한 카테고리 칩
    category_bar()

    with st.container():
        search_col, clear_col = st.columns([4, 1])
        with search_col:
            st.text_input(
                "콘텐츠 검색",
                placeholder="제목이나 본문 키워드를 입력하세요",
                key="content_search_query",
            )
        with clear_col:
            if st.button(
                "초기화",
                type="secondary",
                disabled=not st.session_state.get("content_search_query"),
                key="reset_search_button",
            ):
                st.session_state.content_search_query = ""
                st.experimental_rerun()

    search_query = st.session_state.get("content_search_query", "").strip()

    left, right = st.columns([3, 1])
    with right:
        year_list()

    with left:
        # 연도 파라미터 확인: 2025만 데이터 제공
        try:
            cur_year = st.query_params.get("year")
        except Exception:
            cur_year = st.experimental_get_query_params().get("year")
        if isinstance(cur_year, list):
            cur_year = cur_year[0] if cur_year else None
        if not cur_year:
            cur_year = "2025"

        if str(cur_year) != "2025":
            st.info("선택하신 연도의 자료는 준비 중입니다. 현재는 2025년 자료만 제공됩니다.")
            # 현재 분류 유지한 채 2025로 이동할 수 있는 링크 제공
            cur_cat = st.session_state.get("selected_category", "all")
            if st.button("2025 자료 보기", type="primary"):
                try:
                    st.query_params.update({"page": "main", "year": "2025", "cat": cur_cat})
                except Exception:
                    st.experimental_set_query_params(page="main", year="2025", cat=cur_cat)
                st.rerun()
            return

        # 필터링된 콘텐츠
        cat = st.session_state.get("selected_category", "all")
        if search_query:
            items = search_contents(search_query, category_key=cat)
            st.caption(f"검색 결과 {len(items)}건")
        else:
            items = get_contents(cat)
        if not items:
            st.info("조건에 맞는 콘텐츠를 찾을 수 없습니다.")
            return
        labels_lookup = {k: v for k, v in CATEGORIES}
        n_cols = 3
        rows = (len(items) + n_cols - 1) // n_cols
        card_index = 0
        for _ in range(rows):
            cols = st.columns(n_cols, gap="large")
            for col in cols:
                if card_index >= len(items):
                    break
                item = items[card_index]
                card_index += 1

                label_text = labels_lookup.get(item.get("category", ""), item.get("category", ""))
                title_text = item.get("title", "제목 미정")
                summary_text = item.get("summary") or "자세히 보기에서 주요 내용을 확인하세요."
                summary_text = " ".join(summary_text.split())
                if len(summary_text) > 120:
                    summary_text = summary_text[:117] + "..."

                detail_url = f"?page=detail&content_id={item.get('id')}"
                image_url = item.get("img")
                if image_url:
                    media_block = f'<img src="{html.escape(image_url)}" alt="{html.escape(title_text)}" loading="lazy" />'
                else:
                    placeholder_label = html.escape((label_text or "Insight")[:8] or "Insight")
                    media_block = f'<div class="no-image">{placeholder_label}</div>'

                card_html = f"""
                <div class="content-card">
                  <div class="content-card-content">
                    <span class="badge">{html.escape(label_text or '')}</span>
                    {media_block}
                    <h4>{html.escape(title_text)}</h4>
                    <p>{html.escape(summary_text)}</p>
                    <a class="cta" href="{html.escape(detail_url)}" target="_self">자세히 보기</a>
                  </div>
                </div>
                """

                with col:
                    st.markdown(card_html, unsafe_allow_html=True)
