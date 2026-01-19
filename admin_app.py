import streamlit as st

from src.styles import global_css
from src.workspace import render_workspace

FEATURED_TITLE = "미래사회의 문턱에서 한국의 교육 훈련 돌봄 체계는 어떻게 재정렬되고 있는가"

st.set_page_config(
    page_title=f"KOSSDA 데이터 워크스페이스 (Admin) | {FEATURED_TITLE}",
    page_icon="🛠️",
    layout="wide",
)
st.markdown(global_css(), unsafe_allow_html=True)

render_workspace(admin_mode=True)
