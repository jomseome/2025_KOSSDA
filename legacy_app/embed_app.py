from __future__ import annotations

import streamlit as st
from plotly.io import to_html

from src.custom_visuals import covid_section2_chart, covid_section3_chart
from src.styles import global_css

st.set_page_config(
    page_title="KOSSDA 임베드 도구",
    page_icon="🔗",
    layout="wide",
)
st.markdown(global_css(), unsafe_allow_html=True)

st.title("블로그 임베드를 위한 COVID-19 시각화")
st.caption(
    "아래에서 그래프를 선택하면 반응형 Plotly HTML 코드를 생성합니다. "
    "블로그 플랫폼의 HTML 편집기에 코드를 붙여넣으면 동일한 그래프를 임베드할 수 있습니다."
)

embed_mode = st.radio(
    "Plotly 스크립트 포함 방식",
    options=["CDN (인터넷 필요)", "파일에 포함 (오프라인 가능)"],
    index=0,
    horizontal=True,
    help="CDN 모드는 파일이 가볍지만 인터넷 연결이 필요합니다. "
    "파일에 포함을 선택하면 Plotly JS를 한 번에 포함하므로 다른 컴퓨터에서도 그대로 열 수 있습니다.",
)
include_plotlyjs = "inline" if "파일" in embed_mode else "cdn"


def _build_embed_html(fig, container_id: str, include_plotlyjs: str) -> tuple[str, str]:
    """Return responsive Plotly snippet plus standalone HTML document."""
    base_html = to_html(
        fig,
        include_plotlyjs=include_plotlyjs,
        full_html=False,
        config={"responsive": True, "displaylogo": False},
    )
    snippet = (
        f"<div id=\"{container_id}\" style=\"width:100%;max-width:960px;margin:auto;\">"
        f"{base_html}</div>"
    )
    full_doc = (
        "<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'/>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'/>"
        "<title>Plotly Embed</title></head><body style='margin:0;padding:24px;background:#f8fafc;'>"
        f"{snippet}</body></html>"
    )
    return snippet, full_doc


CHARTS = [
    {
        "key": "covid_section2",
        "label": "세계 주요 도시 추세와 비교: 전국 vs 서울",
        "renderer": covid_section2_chart,
        "slug": "covid19",
        "slot": "slot-1",
        "description": "코로나19 이후 범죄 지표의 전국과 서울 비교선.",
    },
    {
        "key": "covid_section3",
        "label": "한국 범죄유형별 변화에 영향을 준 사회지출 흐름",
        "renderer": covid_section3_chart,
        "slug": "covid19",
        "slot": "slot-2",
        "description": "사회지출 비중 변화가 범죄 추세에 미친 영향을 보여주는 영역 그래프.",
    },
]

tab_labels = [chart["label"] for chart in CHARTS]
tabs = st.tabs(tab_labels)

for chart, tab in zip(CHARTS, tabs):
    with tab:
        st.subheader(chart["label"])
        st.caption(chart["description"])

        fig = chart["renderer"](chart["slug"], chart["slot"])
        st.plotly_chart(fig, use_container_width=True, key=f"preview_{chart['key']}")

        snippet_html, full_html = _build_embed_html(
            fig,
            container_id=f"embed-{chart['key']}",
            include_plotlyjs=include_plotlyjs,
        )

        st.markdown("**HTML 코드**")
        st.text_area(
            label="복사해서 블로그 HTML 편집기에 붙여넣으세요.",
            value=snippet_html,
            height=260,
            key=f"embed_text_{chart['key']}",
        )

        st.download_button(
            label="단일 HTML 파일 다운로드",
            data=full_html,
            file_name=f"{chart['key']}_embed.html",
            mime="text/html",
            key=f"download_{chart['key']}",
        )

        st.info(
            "임베드 후 레이아웃 문제가 생기면, 블로그 편집기에서 컨테이너 폭을 100%로 유지하거나 "
            "iframe/HTML 위젯을 사용하세요."
        )
