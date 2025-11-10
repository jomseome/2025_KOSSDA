from __future__ import annotations

from typing import Dict, List, Optional, Any

import pandas as pd
import plotly.express as px


def _apply_filters(df: pd.DataFrame, filters: Optional[Dict[str, Any]]) -> pd.DataFrame:
    if not filters:
        return df
    filtered = df.copy()
    for column, value in filters.items():
        if column not in filtered.columns:
            continue
        if isinstance(value, (list, tuple, set)):
            filtered = filtered[filtered[column].isin(list(value))]
        else:
            filtered = filtered[filtered[column] == value]
    return filtered


def _resolve_column(column: Any, transform: Optional[Dict[str, Any]]) -> Any:
    if column is None:
        return None
    if transform is None:
        return column
    rename_map: Dict[Any, Any] = transform.get("rename", {}) if isinstance(transform, dict) else {}
    renamed = rename_map.get(column, column)
    rename_after = transform.get("rename_after_scale", {}) if isinstance(transform, dict) else {}
    renamed = rename_after.get(renamed, renamed)
    return renamed


def _apply_transform(df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
    result = df.copy()

    if "row_range" in transform:
        start, end = transform["row_range"]
        iloc_start = int(start) if start is not None else None
        iloc_end = int(end) if end is not None else None
        if iloc_start is not None or iloc_end is not None:
            result = result.iloc[
                iloc_start if iloc_start is not None else 0 : (iloc_end + 1) if iloc_end is not None else None
            ]

    if "slice_rows" in transform:
        start, end = transform["slice_rows"]
        result = result.loc[start:end]

    if "rename" in transform and isinstance(transform["rename"], dict):
        result = result.rename(columns=transform["rename"])

    if "use_columns" in transform:
        keep_spec = transform["use_columns"]
        keep: List[Any] = []
        for col in keep_spec:
            if isinstance(col, int):
                if 0 <= col < len(result.columns):
                    keep.append(result.columns[col])
            elif col in result.columns:
                keep.append(col)
        if keep:
            result = result.loc[:, keep]

    result = result.loc[:, ~result.columns.duplicated()]

    if "to_numeric" in transform:
        for col in transform["to_numeric"]:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors="coerce")

    if "scale" in transform:
        for col, factor in transform["scale"].items():
            if col in result.columns:
                result[col] = result[col] * factor

    if "rename_after_scale" in transform and isinstance(transform["rename_after_scale"], dict):
        result = result.rename(columns=transform["rename_after_scale"])

    if "dropna" in transform:
        drop_conf = transform["dropna"]
        if drop_conf is True:
            result = result.dropna()
        elif isinstance(drop_conf, list):
            subset = [col for col in drop_conf if col in result.columns]
            if subset:
                result = result.dropna(subset=subset)

    if "sort_by" in transform and isinstance(transform["sort_by"], dict):
        by = transform["sort_by"].get("column")
        ascending = transform["sort_by"].get("ascending", True)
        if by in result.columns:
            result = result.sort_values(by=by, ascending=ascending)

    return result.reset_index(drop=True)


def prepare_chart_dataframe(df: pd.DataFrame, meta: Dict[str, Any]) -> tuple[pd.DataFrame, Any, List[Any], Optional[str]]:
    working = df.copy()
    filters = meta.get("filters")
    working = _apply_filters(working, filters)

    transform = meta.get("transform")
    if isinstance(transform, dict):
        working = _apply_transform(working, transform)
        # re-apply filters if 컬럼명이 변환된 경우
        working = _apply_filters(working, filters)

    x_col = _resolve_column(meta.get("x"), transform)
    y_cols = meta.get("y")
    if not isinstance(y_cols, list) or not y_cols:
        raise ValueError("세로축(Y) 정보가 필요합니다.")
    resolved_y = [_resolve_column(col, transform) for col in y_cols]
    color_col = _resolve_column(meta.get("color"), transform)

    return working, x_col, resolved_y, color_col


def build_chart(df: pd.DataFrame, meta: Dict[str, Any]):
    chart_type = str(meta.get("chart_type", ""))
    data, x_col, y_cols, color_col = prepare_chart_dataframe(df, meta)
    labels = meta.get("labels") if isinstance(meta.get("labels"), dict) else None

    if x_col not in data.columns:
        raise ValueError(f"X축 컬럼 '{x_col}'을(를) 찾을 수 없습니다.")
    for col in y_cols:
        if col not in data.columns:
            raise ValueError(f"Y축 컬럼 '{col}'을(를) 찾을 수 없습니다.")

    color_arg: Optional[str] = color_col if isinstance(color_col, str) else None

    if chart_type == "선":
        fig = px.line(
            data,
            x=x_col,
            y=y_cols,
            color=color_arg,
            markers=True,
            labels=labels,
        )
    elif chart_type == "영역":
        fig = px.area(
            data,
            x=x_col,
            y=y_cols,
            color=color_arg,
            labels=labels,
        )
    elif chart_type == "막대":
        fig = px.bar(
            data,
            x=x_col,
            y=y_cols if len(y_cols) > 1 else y_cols[0],
            color=color_arg,
            barmode="group" if len(y_cols) > 1 else "relative",
            labels=labels,
        )
    elif chart_type == "산점도":
        size_arg: Optional[str] = None
        first_y = y_cols[0]
        if pd.api.types.is_numeric_dtype(data[first_y]):
            size_arg = first_y
        fig = px.scatter(
            data,
            x=x_col,
            y=first_y,
            color=color_arg,
            size=size_arg,
            labels=labels,
        )
    else:
        raise ValueError(f"지원하지 않는 차트 유형입니다: {chart_type}")

    return fig
