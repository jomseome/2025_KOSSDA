from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path("Data/excel_data/sample_story_points.xlsx")


@lru_cache(maxsize=4)
def _load_dataset() -> Dict[str, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"샘플 데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
    excel = pd.ExcelFile(DATA_PATH)
    return {name: excel.parse(name) for name in excel.sheet_names}


def _ensure_dataset(sheet: str) -> pd.DataFrame:
    data_map = _load_dataset()
    if sheet not in data_map:
        raise KeyError(f"시트 `{sheet}`을(를) 찾을 수 없습니다.")
    return data_map[sheet]


def covid_section2_chart(story_slug: str, slot_id: str) -> go.Figure:
    df = _ensure_dataset("crime_trend")
    fig = px.line(
        df,
        x="year",
        y=["전국", "서울"],
        markers=True,
        color_discrete_map={
            "전국": "#1565C0",  # deep blue
            "서울": "#0D47A1",  # slightly darker blue for contrast
        },
        title="세계 주요 도시 추세와 비교: 전국 vs 서울",
    )
    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="1인당 지표",
        font={"family": "Noto Sans KR, Noto Sans, sans-serif"},
    )
    return fig


def covid_section3_chart(story_slug: str, slot_id: str) -> go.Figure:
    df = _ensure_dataset("welfare_overview")
    fig = px.area(
        df,
        x="year",
        y="사회지출(GDP%)",
        title="한국 범죄유형별 변화에 영향을 준 사회지출 흐름",
    )
    fig.update_traces(
        line={"color": "#0D47A1", "width": 3},
        fillcolor="rgba(21, 101, 192, 0.25)",  # light blue fill
    )
    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="사회지출(GDP%)",
        font={"family": "Noto Sans KR, Noto Sans, sans-serif"},
    )
    return fig


def covid_interactive_panel(story_slug: str) -> None:
    df_crime = _ensure_dataset("crime_trend")
    df_welfare = _ensure_dataset("welfare_overview")

    st.markdown("#### 데이터 탐색")
    st.caption("연도 범위를 조정하거나 항목을 골라서 살펴보세요.")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox("범죄 지표", options=["전국", "서울", "부산"], key="covid_metric")
        with col2:
            year_range = st.slider(
                "연도 범위",
                min_value=int(df_crime["year"].min()),
                max_value=int(df_crime["year"].max()),
                value=(2014, 2024),
            )

    mask = df_crime["year"].between(*year_range)
    fig = px.line(
        df_crime[mask],
        x="year",
        y=metric,
        markers=True,
        title=f"{metric} 범죄 지표 추세",
    )
    fig.update_layout(xaxis_title="연도", yaxis_title="지표 값")
    st.plotly_chart(fig, use_container_width=True, key="covid_interactive_crime")

    st.markdown("##### 복지 지표와 비교")
    fig_welfare = px.area(
        df_welfare[mask],
        x="year",
        y=["사회지출(GDP%)", "빈곤율(%)"],
        title="사회지출과 빈곤율",
    )
    fig_welfare.update_layout(xaxis_title="연도")
    st.plotly_chart(fig_welfare, use_container_width=True, key="covid_interactive_welfare")


VISUAL_RENDERERS = {
    "covid_section2_chart": covid_section2_chart,
    "covid_section3_chart": covid_section3_chart,
}


INTERACTIVE_PANELS = {
    "covid19": covid_interactive_panel,
}
