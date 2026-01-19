from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

DATA_PATH = Path("Data/excel_data/sample_story_points.xlsx")
EDUCATION_CARE_PATH = Path(
    "Data/excel_data/(임시본)교육훈련 및 돌봄분야 데이터 모음.xlsx"
)

EDUCATION_CARE_SHEETS = {
    1: "그림1. 학령아동 변동 추계",
    2: "그림2. OECD 교사 1인당 학생 수",
    3: "그림3. 한국과 OECD의 학급당 학생 수",
    4: "그림4. 한국과 OECD의 교육단계별 GDP 대비 공교육",
    5: "그림5. 한국과 OECD의 국제 학업성취도 평가 결과",
    6: "그림6. 한국과 OECD의 수학 점수에서의 학교 내 및 ",
    7: "그림7. 교육단계별 학생 1인당 월평균 사교육비",
    8: "그림8. OECD 국가 간 사교육 참여 수준 비교",
    9: "그림9. 초·중·고등학교에 대한 평가",
    10: "그림10.  학생들의 학업스트레스 정도",
    11: "그림11. 학생들의 학업스트레스 이유(복수응답)",
    12: "그림12. OECD 주요 참여국 학생들의 학업 관련 불안",
    13: "그림13. OECD 주요국의 학부모 학교교육만족도",
    14: "그림14. 교육수준별 전공직업일치도",
    15: "그림15. 보육·교육기관 만족도",
    16: "그림16. 국가별 학교 밖 신체활동을 하지 않는 학생 비",
}


@lru_cache(maxsize=4)
def _load_dataset() -> Dict[str, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"샘플 데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
    excel = pd.ExcelFile(DATA_PATH)
    return {name: excel.parse(name) for name in excel.sheet_names}


@lru_cache(maxsize=2)
def _load_education_care_dataset() -> Dict[str, pd.DataFrame]:
    if not EDUCATION_CARE_PATH.exists():
        raise FileNotFoundError(f"교육·돌봄 데이터 파일을 찾을 수 없습니다: {EDUCATION_CARE_PATH}")
    excel = pd.ExcelFile(EDUCATION_CARE_PATH)
    return {name: excel.parse(name) for name in excel.sheet_names}


def _education_care_sheet(sheet: str) -> pd.DataFrame:
    data_map = _load_education_care_dataset()
    if sheet not in data_map:
        raise KeyError(f"시트 `{sheet}`을(를) 찾을 수 없습니다.")
    return data_map[sheet]


def _parse_year(value) -> float:
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return int(value)
    match = re.search(r"(\d{4})", str(value).strip())
    return int(match.group(1)) if match else np.nan


def _apply_common_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        hovermode="closest",
        legend_title_text="",
        margin=dict(l=40, r=20, t=70, b=40),
    )
    return fig


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


def education_care_fig01(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[1]).rename(columns={"Unnamed: 0": "구분"})
    long = df.melt(id_vars=["구분"], var_name="연도", value_name="학령아동(천명)")
    long["연도"] = long["연도"].apply(_parse_year)
    long = long.dropna(subset=["연도"])
    long["연도"] = long["연도"].astype(int)

    fig = px.line(
        long,
        x="연도",
        y="학령아동(천명)",
        color="구분",
        markers=True,
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[1])


def education_care_fig02(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[2]).copy()
    df["기준연도"] = df["기준연도"].ffill()
    df["기준연도"] = df["기준연도"].apply(_parse_year)
    df = df.dropna(subset=["기준연도"])
    df["기준연도"] = df["기준연도"].astype(int)
    long = df.melt(
        id_vars=["기준연도", "구분"],
        var_name="학교급",
        value_name="교사1인당학생수",
    )

    fig = px.line(
        long,
        x="기준연도",
        y="교사1인당학생수",
        color="구분",
        line_dash="학교급",
        markers=True,
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[2])


def education_care_fig03(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[3]).copy()
    df["기준연도"] = df["기준연도"].ffill()
    df["기준연도"] = df["기준연도"].apply(_parse_year)
    df = df.dropna(subset=["기준연도"])
    df["기준연도"] = df["기준연도"].astype(int)
    long = df.melt(
        id_vars=["기준연도", "구분"],
        var_name="학교급",
        value_name="학급당학생수",
    )

    fig = px.line(
        long,
        x="기준연도",
        y="학급당학생수",
        color="구분",
        line_dash="학교급",
        markers=True,
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[3])


def education_care_fig04(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[4]).copy()

    sub = df.iloc[0].tolist()
    df2 = df.iloc[1:].copy()

    new_cols = []
    for idx, col in enumerate(df2.columns):
        if col == "구분":
            new_cols.append(("구분", "구분"))
        else:
            stage = df.columns[idx]
            sector = sub[idx]
            new_cols.append((stage, sector))

    df2.columns = pd.MultiIndex.from_tuples(new_cols)
    df2 = df2.rename(columns={("구분", "구분"): "국가"})
    df2.columns = ["국가" if isinstance(col, tuple) and col[0] == "구분" else col for col in df2.columns]

    records = []
    for col in df2.columns:
        if col == "국가":
            continue
        stage, sector = col
        tmp = df2[["국가"]].copy()
        tmp["교육단계"] = stage
        tmp["재원"] = sector
        tmp["GDP대비비율(%)"] = df2[col].astype(float)
        records.append(tmp)
    long = pd.concat(records, ignore_index=True)

    fig = px.bar(
        long,
        x="교육단계",
        y="GDP대비비율(%)",
        color="재원",
        barmode="group",
        facet_col="국가",
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[4])


def education_care_fig05(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[5]).copy()
    df["연도"] = df["연도"].ffill().apply(_parse_year)
    df = df.dropna(subset=["연도"])
    df["연도"] = df["연도"].astype(int)
    long = df.melt(
        id_vars=["연도", "영역"],
        value_vars=["한국", "OECD 평균"],
        var_name="구분",
        value_name="점수",
    )

    fig = px.bar(
        long,
        x="영역",
        y="점수",
        color="구분",
        barmode="group",
        facet_col="연도",
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[5])


def education_care_fig06(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[6]).copy()
    hdr = df.iloc[0].tolist()
    df2 = df.iloc[1:].copy()
    df2 = df2.rename(columns={"Unnamed: 0": "지표"})

    mapping = {
        df2.columns[1]: ("대한민국", _parse_year(hdr[1])),
        df2.columns[2]: ("대한민국", _parse_year(hdr[2])),
        df2.columns[3]: ("OECD 평균", _parse_year(hdr[3])),
        df2.columns[4]: ("OECD 평균", _parse_year(hdr[4])),
    }

    records = []
    for col, (country, year) in mapping.items():
        tmp = df2[["지표"]].copy()
        tmp["국가"] = country
        tmp["연도"] = int(year)
        tmp["비율(%)"] = df2[col].astype(float)
        records.append(tmp)
    long = pd.concat(records, ignore_index=True)

    fig = px.bar(
        long,
        x="지표",
        y="비율(%)",
        color="국가",
        barmode="group",
        facet_col="연도",
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[6])


def education_care_fig07(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[7]).rename(columns={"Unnamed: 0": "학교급"})
    long = df.melt(id_vars=["학교급"], var_name="연도", value_name="월평균사교육비(만원)")
    long["연도"] = long["연도"].apply(_parse_year)
    long = long.dropna(subset=["연도"])
    long["연도"] = long["연도"].astype(int)

    fig = px.line(
        long,
        x="연도",
        y="월평균사교육비(만원)",
        color="학교급",
        markers=True,
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[7])


def education_care_fig08(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[8]).copy()
    df = df.sort_values("사교육 참여수준", ascending=True)
    df["하이라이트"] = np.where(df["국가"] == "한국", "한국", "기타")

    fig = px.bar(
        df,
        x="사교육 참여수준",
        y="국가",
        orientation="h",
        color="하이라이트",
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[8])


def education_care_fig09(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[9]).copy()
    df["평가대상"] = df["평가대상"].ffill()
    df["라벨"] = df["평가대상"] + " | " + df["구분"].astype(str)

    dist_cols = ["매우 잘하고 있다", "잘하고 있다", "보통이다", "못하고 있다", "전혀 못하고 있다"]
    long = df.melt(id_vars=["라벨"], value_vars=dist_cols, var_name="응답", value_name="비율(%)")

    fig = px.bar(
        long,
        x="라벨",
        y="비율(%)",
        color="응답",
        barmode="stack",
    )
    fig.update_xaxes(tickangle=45)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[9])


def education_care_fig10(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[10]).copy()
    dist_cols = ["상당히 그렇다", "어느정도 그렇다", "보통이다", "별로 그렇지 않다", "전혀 그렇지 않다"]
    long = df.melt(id_vars=["구분"], value_vars=dist_cols, var_name="응답", value_name="비율(%)")

    fig = px.bar(long, x="구분", y="비율(%)", color="응답", barmode="stack")
    fig.update_xaxes(tickangle=0)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[10])


def education_care_fig11(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[11]).copy()
    long = df.melt(id_vars=["구분"], var_name="이유", value_name="비율(%)")

    fig = px.bar(
        long,
        x="이유",
        y="비율(%)",
        color="구분",
        barmode="group",
    )
    fig.update_xaxes(tickangle=35)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[11])


def education_care_fig12(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[12]).copy()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df["국가"],
            y=df["시험을 잘 준비했더라도 불안하다"],
            name="시험 준비해도 불안(%)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=df["국가"],
            y=df["공부를 할 때 매우 긴장된다"],
            name="공부할 때 매우 긴장(%)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df["국가"],
            y=df["학업 관련 불안감 지수"],
            name="학업 불안감 지수",
            mode="lines+markers",
        ),
        secondary_y=True,
    )

    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="비율(%)", secondary_y=False)
    fig.update_yaxes(title_text="지수", secondary_y=True)
    fig.update_xaxes(tickangle=25)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[12])


def education_care_fig13(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[13]).rename(columns={"Unnamed: 0": "국가"})
    long = df.melt(id_vars=["국가"], var_name="연도", value_name="만족도(점)")
    long["연도"] = long["연도"].apply(_parse_year)
    long = long.dropna(subset=["연도"])
    long["연도"] = long["연도"].astype(int)

    fig = px.line(long, x="연도", y="만족도(점)", color="국가", markers=True)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[13])


def education_care_fig14(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[14]).rename(columns={"Unnamed: 0": "교육수준"})
    long = df.melt(id_vars=["교육수준"], var_name="연도", value_name="전공-직업일치도(%)")
    long["연도"] = long["연도"].apply(_parse_year)
    long = long.dropna(subset=["연도"])
    long["연도"] = long["연도"].astype(int)

    fig = px.line(long, x="연도", y="전공-직업일치도(%)", color="교육수준", markers=True)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[14])


def education_care_fig15(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[15]).copy()
    df["연도"] = df["구분"].apply(_parse_year)
    df = df.dropna(subset=["연도"])
    df["연도"] = df["연도"].astype(int)
    long = df.drop(columns=["구분"]).melt(id_vars=["연도"], var_name="기관유형", value_name="만족도(%)")

    fig = px.line(long, x="연도", y="만족도(%)", color="기관유형", markers=True)
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[15])


def education_care_fig16(story_slug: str, slot_id: str) -> go.Figure:
    df = _education_care_sheet(EDUCATION_CARE_SHEETS[16]).rename(columns={"Unnamed: 0": "국가"}).copy()
    df = df.sort_values("Girls", ascending=False)
    long = df.melt(id_vars=["국가"], value_vars=["Boys", "Girls"], var_name="성별", value_name="미참여율(%)")

    fig = px.bar(
        long,
        x="미참여율(%)",
        y="국가",
        color="성별",
        orientation="h",
        barmode="group",
    )
    return _apply_common_layout(fig, EDUCATION_CARE_SHEETS[16])


VISUAL_RENDERERS = {
    "covid_section2_chart": covid_section2_chart,
    "covid_section3_chart": covid_section3_chart,
    "education_care_fig01": education_care_fig01,
    "education_care_fig02": education_care_fig02,
    "education_care_fig03": education_care_fig03,
    "education_care_fig04": education_care_fig04,
    "education_care_fig05": education_care_fig05,
    "education_care_fig06": education_care_fig06,
    "education_care_fig07": education_care_fig07,
    "education_care_fig08": education_care_fig08,
    "education_care_fig09": education_care_fig09,
    "education_care_fig10": education_care_fig10,
    "education_care_fig11": education_care_fig11,
    "education_care_fig12": education_care_fig12,
    "education_care_fig13": education_care_fig13,
    "education_care_fig14": education_care_fig14,
    "education_care_fig15": education_care_fig15,
    "education_care_fig16": education_care_fig16,
}


INTERACTIVE_PANELS = {
    "covid19": covid_interactive_panel,
}
