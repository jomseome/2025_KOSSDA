import streamlit as st

from src.styles import global_css
from src.viewer import render_public_view

st.set_page_config(
    page_title="KOSSDA 데이터 스토리",
    page_icon="📊",
    layout="wide",
)
st.markdown(global_css(), unsafe_allow_html=True)

render_public_view()
