from typing import Callable, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

from ..content_loader import get_content
from ..data import CATEGORIES
from ..ui import top_blue_bar
from .registry import page


@page(
    "detail",
    title="콘텐츠 상세",
    description="선택된 콘텐츠 상세 시각화",
)
def render(context: dict | None = None):
    context = context or {}
    content_id = context.get("content_id")
    go_main_callback = context.get("go_main")
    top_blue_bar()

    item = get_content(content_id) if content_id else None
    if not item:
        st.warning("콘텐츠를 찾을 수 없습니다.")
        if st.button("메인으로") and callable(go_main_callback):
            go_main_callback()
        return

    st.markdown("---")
    category_label = next((v for k,v in CATEGORIES if k == item.get("category")), item.get("category"))
    row_left, row_right = st.columns([6, 1])
    with row_left:
        st.markdown(f"**{category_label}**")
    with row_right:
        st.markdown("<div style='text-align:right'><a class='back-btn' href='?page=main' target='_self'>← 목록으로</a></div>", unsafe_allow_html=True)
    st.markdown(f"## {item.get('title')}")

    # 본문 (마크다운)
    body = item.get("body_text")
    if body:
        st.markdown(body)

    visualizer = _VISUALIZERS.get(item.get("id"))
    if visualizer:
        visualizer()


def _render_migrant_increase() -> None:
    df = pd.DataFrame(
        {
            "연도": list(range(2010, 2025, 3)),
            "외국인 근로자": [32.4, 45.6, 58.2, 71.5, 86.4],
            "결혼 이민자": [7.8, 10.6, 13.4, 15.9, 18.7],
            "유학생": [4.2, 6.5, 8.1, 9.8, 11.6],
        }
    )
    melted = df.melt(id_vars="연도", var_name="구분", value_name="만 명")
    fig = px.area(
        melted,
        x="연도",
        y="만 명",
        color="구분",
        line_group="구분",
        markers=True,
        title="체류 자격별 국제이주 인구 추세 (예시)",
    )
    fig.update_traces(mode="lines+markers", hovertemplate="%{x}년<br>%{legendgroup}: %{y}만 명")
    fig.update_layout(legend_title="구분")
    st.plotly_chart(fig, width="stretch")

    st.download_button(
        "예시 데이터 다운로드 (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="international_migration_sample.csv",
        mime="text/csv",
        type="primary",
    )


def _render_aging_society() -> None:
    population = pd.DataFrame(
        {
            "연도": [2020, 2025, 2030, 2035, 2040],
            "고령인구": [850, 1010, 1230, 1470, 1660],
            "생산가능인구": [3610, 3490, 3300, 3120, 2950],
            "유소년": [690, 650, 610, 580, 560],
        }
    )
    melted = population.melt(id_vars="연도", var_name="연령대", value_name="천 명")
    fig_pop = px.area(
        melted,
        x="연도",
        y="천 명",
        color="연령대",
        title="연령대별 인구 구조 전망 (예시)",
    )
    fig_pop.update_traces(hovertemplate="%{x}년<br>%{legendgroup}: %{y}천 명")
    st.plotly_chart(fig_pop, width="stretch")

    dependency = pd.DataFrame(
        {
            "연도": [2020, 2025, 2030, 2035, 2040],
            "노년부양비": [24, 30, 38, 51, 58],
            "의료·돌봄 지출": [42, 51, 63, 79, 95],
        }
    )
    fig_dep = px.bar(
        dependency,
        x="연도",
        y=["노년부양비", "의료·돌봄 지출"],
        barmode="group",
        title="노년부양비와 고령층 관련 지출 추이 (예시)",
        labels={"value": "지표", "variable": "항목", "연도": "연도"},
    )
    fig_dep.update_traces(hovertemplate="%{x}년<br>%{fullData.name}: %{y}")
    st.plotly_chart(fig_dep, width="stretch")

    st.download_button(
        "예시 데이터 다운로드 (CSV)",
        data=population.merge(dependency, on="연도").to_csv(index=False).encode("utf-8-sig"),
        file_name="aging_society_sample.csv",
        mime="text/csv",
    )


def _render_social_conflict() -> None:
    conflict = pd.DataFrame(
        {
            "연도": [2018, 2019, 2020, 2021, 2022, 2023],
            "세대": [38, 41, 44, 47, 52, 55],
            "소득": [42, 44, 46, 50, 53, 57],
            "지역": [28, 30, 33, 36, 39, 43],
            "이주배경": [24, 27, 31, 36, 41, 45],
        }
    )
    melted = conflict.melt(id_vars="연도", var_name="갈등 영역", value_name="갈등 체감 지수")
    fig_line = px.line(
        melted,
        x="연도",
        y="갈등 체감 지수",
        color="갈등 영역",
        markers=True,
        title="갈등 체감 지수 변화 (예시)",
    )
    fig_line.update_traces(hovertemplate="%{x}년<br>%{legendgroup}: %{y}점")
    st.plotly_chart(fig_line, width="stretch")

    by_group = pd.DataFrame(
        {
            "집단": ["청년", "여성", "이주민", "고령층"],
            "차별 경험률": [34, 29, 46, 18],
            "갈등 회피 응답": [22, 19, 27, 31],
        }
    )
    fig_bar = px.bar(
        by_group,
        x="집단",
        y=["차별 경험률", "갈등 회피 응답"],
        barmode="group",
        title="집단별 차별 경험과 갈등 회피 (예시)",
        labels={"value": "%", "variable": "지표"},
    )
    fig_bar.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y}%")
    st.plotly_chart(fig_bar, width="stretch")

    st.download_button(
        "예시 데이터 다운로드 (CSV)",
        data=melted.to_csv(index=False).encode("utf-8-sig"),
        file_name="social_conflict_sample.csv",
        mime="text/csv",
    )


def _render_human_resources() -> None:
    supply_demand = pd.DataFrame(
        {
            "기술 분야": ["반도체", "AI", "이차전지", "바이오", "양자"] * 2,
            "지표": ["수요", "수요", "수요", "수요", "수요", "공급", "공급", "공급", "공급", "공급"],
            "인력 지수": [92, 88, 83, 76, 70, 64, 55, 48, 52, 38],
        }
    )
    fig_radar = px.line_polar(
        supply_demand,
        r="인력 지수",
        theta="기술 분야",
        color="지표",
        line_close=True,
        title="전략 기술 분야 인력 수요·공급 지수 (예시)",
    )
    fig_radar.update_traces(hovertemplate="%{theta}<br>%{legendgroup}: %{r}")
    st.plotly_chart(fig_radar, width="stretch")

    retention = pd.DataFrame(
        {
            "기업 유형": ["국내 대기업", "국내 중견", "글로벌 기업", "스타트업"],
            "1년 이직률": [12, 18, 9, 24],
            "기술 교육 투자": [3.1, 1.8, 4.2, 2.6],
        }
    )
    fig_scatter = px.scatter(
        retention,
        x="기술 교육 투자",
        y="1년 이직률",
        size="1년 이직률",
        text="기업 유형",
        title="기업 유형별 교육 투자와 이직률 (예시)",
        labels={"기술 교육 투자": "1인당 교육 투자 (백만원)", "1년 이직률": "%"},
    )
    fig_scatter.update_traces(hovertemplate="%{text}<br>투자 %{x}백만원<br>이직률 %{y}%")
    st.plotly_chart(fig_scatter, width="stretch")

    st.download_button(
        "예시 데이터 다운로드 (CSV)",
        data=supply_demand.to_csv(index=False).encode("utf-8-sig"),
        file_name="tech_talent_gap_sample.csv",
        mime="text/csv",
    )


def _render_labor_market() -> None:
    employment = pd.DataFrame(
        {
            "연도": [2018, 2019, 2020, 2021, 2022, 2023],
            "정규직": [70, 69, 66, 65, 64, 63],
            "비정규직": [24, 25, 27, 27, 28, 28],
            "플랫폼": [6, 6, 7, 8, 8, 9],
        }
    )
    melted = employment.melt(id_vars="연도", var_name="고용 형태", value_name="비중")
    fig_area = px.area(
        melted,
        x="연도",
        y="비중",
        color="고용 형태",
        groupnorm="percent",
        title="고용 형태별 비중 변화 (예시)",
    )
    fig_area.update_traces(hovertemplate="%{x}년<br>%{legendgroup}: %{y:.1f}%")
    st.plotly_chart(fig_area, width="stretch")

    wages = pd.DataFrame(
        {
            "직무": ["데이터", "제조 자동화", "헬스케어", "물류", "콘텐츠"],
            "상위 25% 임금": [7200, 6400, 5800, 5100, 4900],
            "하위 25% 임금": [3600, 3100, 2800, 2400, 2300],
        }
    )
    fig_wage = px.bar(
        wages.melt(id_vars="직무", var_name="분위", value_name="연봉"),
        x="직무",
        y="연봉",
        color="분위",
        barmode="group",
        title="직무별 연봉 격차 (예시)",
        labels={"연봉": "만원"},
    )
    fig_wage.update_traces(hovertemplate="%{x}<br>%{legendgroup}: %{y}만원")
    st.plotly_chart(fig_wage, width="stretch")

    st.download_button(
        "예시 데이터 다운로드 (CSV)",
        data=employment.to_csv(index=False).encode("utf-8-sig"),
        file_name="labor_market_sample.csv",
        mime="text/csv",
    )


def _render_income_inequality() -> None:
    quintiles = pd.DataFrame(
        {
            "연도": [2015, 2017, 2019, 2021, 2023],
            "상위 20%": [46, 47, 48, 49, 50],
            "중위 40%": [36, 35, 35, 34, 34],
            "하위 40%": [18, 18, 17, 17, 16],
        }
    )
    melted = quintiles.melt(id_vars="연도", var_name="소득 분위", value_name="소득 점유율")
    fig_stack = px.area(
        melted,
        x="연도",
        y="소득 점유율",
        color="소득 분위",
        title="소득 분위별 소득 점유율 추이 (예시)",
    )
    fig_stack.update_traces(hovertemplate="%{x}년<br>%{legendgroup}: %{y}%")
    st.plotly_chart(fig_stack, width="stretch")

    gini = pd.DataFrame(
        {
            "연도": list(range(2015, 2024)),
            "지니계수": [0.331, 0.332, 0.334, 0.336, 0.337, 0.335, 0.338, 0.339, 0.34],
        }
    )
    fig_gini = px.line(
        gini,
        x="연도",
        y="지니계수",
        markers=True,
        title="가처분소득 기준 지니계수 (예시)",
    )
    fig_gini.update_traces(hovertemplate="%{x}년<br>지니계수 %{y:.3f}")
    st.plotly_chart(fig_gini, width="stretch")

    st.download_button(
        "예시 데이터 다운로드 (CSV)",
        data=quintiles.merge(gini, on="연도", how="left").to_csv(index=False).encode("utf-8-sig"),
        file_name="income_inequality_sample.csv",
        mime="text/csv",
    )


_VISUALIZERS: Dict[str, Callable[[], None]] = {
    "migrant-increase": _render_migrant_increase,
    "aging-society": _render_aging_society,
    "social-conflict": _render_social_conflict,
    "human-resources": _render_human_resources,
    "labor-market": _render_labor_market,
    "income-inequality": _render_income_inequality,
}
