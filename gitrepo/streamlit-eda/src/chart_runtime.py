from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pandas as pd
from plotly.graph_objs import Figure

from .chart_builder import build_chart
from .workspace_data import load_workbook, workbook_path_by_name


def _dataframe_from_meta(meta: Dict[str, Any]) -> pd.DataFrame:
    sheet_name = meta.get("sheet")
    if not isinstance(sheet_name, str):
        raise ValueError("시트 정보를 찾을 수 없습니다.")

    uploaded_payload = meta.get("uploaded_data")
    if isinstance(uploaded_payload, dict):
        sheets = uploaded_payload.get("sheets", {})
        sheet_info = sheets.get(sheet_name)
        if sheet_info is None:
            raise ValueError(f"업로드한 데이터에서 시트 `{sheet_name}`을(를) 찾을 수 없습니다.")
        columns = sheet_info.get("columns", [])
        data = sheet_info.get("data", [])
        return pd.DataFrame(data, columns=columns)

    workbook_name = meta.get("workbook")
    if not isinstance(workbook_name, str):
        raise ValueError("워크북 정보를 찾을 수 없습니다.")

    workbook_path = workbook_path_by_name(workbook_name)
    if workbook_path is None:
        raise FileNotFoundError(f"워크북 `{workbook_name}`을(를) 찾을 수 없습니다.")

    sheet_map = load_workbook(str(workbook_path))
    if sheet_name not in sheet_map:
        raise KeyError(f"시트 `{sheet_name}`을(를) 찾을 수 없습니다.")
    return sheet_map[sheet_name]


def build_figure_from_meta(meta: Dict[str, Any]) -> Tuple[Optional[Figure], Optional[str]]:
    try:
        df = _dataframe_from_meta(meta)
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        return None, str(exc)

    try:
        fig = build_chart(df, meta)
    except Exception as exc:  # pragma: no cover
        return None, str(exc)
    return fig, None
