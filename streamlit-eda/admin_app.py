import streamlit as st

from src.styles import global_css
from src.workspace import render_workspace

st.set_page_config(
    page_title="KOSSDA 데이터 워크스페이스 (Admin)",
    page_icon="🛠️",
    layout="wide",
)
st.markdown(global_css(), unsafe_allow_html=True)

render_workspace(admin_mode=True)
