import streamlit as st
import streamlit.components.v1 as components
from .data import CATEGORIES

def top_blue_bar():
    st.markdown(
        """
        <div class="top-bar">
            <a href="?page=landing" target="_self">KOSSDA, ISDS [한국사회, 시선]</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

def category_bar():
    st.markdown("<h3 style='margin:6px 0 10px 0;text-align:center;font-weight:800;'>2025 한국사회, 시선</h3>", unsafe_allow_html=True)

    # 쿼리파라미터 → 선택 동기화
    try:
        cat = st.query_params.get("cat")
    except Exception:
        cat = st.experimental_get_query_params().get("cat")
    if isinstance(cat, list):
        cat = cat[0] if cat else None
    if cat in [k for k, _ in CATEGORIES]:
        st.session_state.selected_category = cat

    # 현재 연도 유지
    try:
        cur_year = st.query_params.get("year")
    except Exception:
        cur_year = st.experimental_get_query_params().get("year")
    if isinstance(cur_year, list):
        cur_year = cur_year[0] if cur_year else None
    if not cur_year:
        cur_year = "2025"

    # 부분 표시용 오프셋 + 버튼으로 이동 (iframe 미사용)
    if "cat_offset" not in st.session_state:
        st.session_state.cat_offset = 0
    show_count = 7
    keys = [k for k, _ in CATEGORIES]
    sel_idx = keys.index(st.session_state.selected_category)
    if sel_idx < st.session_state.cat_offset:
        st.session_state.cat_offset = sel_idx
    elif sel_idx >= st.session_state.cat_offset + show_count:
        st.session_state.cat_offset = sel_idx - show_count + 1
    st.session_state.cat_offset = max(0, min(max(0, len(CATEGORIES) - show_count), st.session_state.cat_offset))

    left_col, mid_col, right_col = st.columns([0.06, 0.88, 0.06])
    with left_col:
        if st.button("‹", key="cat_prev", help="왼쪽으로"):
            st.session_state.cat_offset = max(0, st.session_state.cat_offset - 1)
            st.rerun()
    with right_col:
        if st.button("›", key="cat_next", help="오른쪽으로"):
            st.session_state.cat_offset = min(max(0, len(CATEGORIES) - show_count), st.session_state.cat_offset + 1)
            st.rerun()
    with mid_col:
        start = st.session_state.cat_offset
        end = start + show_count
        visible = CATEGORIES[start:end]
        chips = []
        for key, label in visible:
            active = " active" if key == st.session_state.selected_category else ""
            chips.append(f'<a class="chip{active}" href="?page=main&year={cur_year}&cat={key}" target="_self">{label}</a>')
        st.markdown(f"<div class='chips-row'>{''.join(chips)}</div>", unsafe_allow_html=True)

def year_list():
    st.markdown("#### 연도 선택")
    years = list(range(2025, 2030))
    try:
        cur_year = st.query_params.get("year")
    except Exception:
        cur_year = st.experimental_get_query_params().get("year")
    if isinstance(cur_year, list):
        cur_year = cur_year[0] if cur_year else None
    links = []
    for y in years:
        active = " active" if str(y) == str(cur_year) else ""
        links.append(f'<a class="year-link{active}" href="?page=main&year={y}" target="_self">{y} 한국사회, 시선</a>')
    st.markdown("<div class='year-list'>" + "\n".join(links) + "</div>", unsafe_allow_html=True)
