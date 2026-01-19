from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

import plotly.graph_objects as go


Renderer = Callable[[str, str], go.Figure]
InteractiveRenderer = Callable[[str], None]


def _get_registry() -> Tuple[Dict[str, Renderer], Dict[str, InteractiveRenderer]]:
    try:
        from . import custom_visuals
    except ImportError:  # pragma: no cover
        return {}, {}

    renderers = getattr(custom_visuals, "VISUAL_RENDERERS", {}) or {}
    panels = getattr(custom_visuals, "INTERACTIVE_PANELS", {}) or {}
    return renderers, panels


def render_visual_from_registry(renderer_name: str, story_slug: str, slot_id: str) -> Tuple[Optional[go.Figure], Optional[str]]:
    renderers, _ = _get_registry()
    func = renderers.get(renderer_name)
    if func is None:
        return None, f"렌더러 '{renderer_name}'를 찾을 수 없습니다."
    try:
        fig = func(story_slug, slot_id)
    except Exception as exc:  # pragma: no cover
        return None, str(exc)
    if fig is None:
        return None, "렌더러가 Plotly Figure를 반환하지 않았습니다."
    if not isinstance(fig, go.Figure):
        try:
            fig = go.Figure(fig)
        except Exception:  # pragma: no cover
            return None, "반환값이 Plotly Figure가 아닙니다."
    return fig, None


def render_interactive_panel(story_slug: str) -> bool:
    _, panels = _get_registry()
    func = panels.get(story_slug)
    if func is None:
        return False
    try:
        func(story_slug)
    except Exception as exc:  # pragma: no cover
        import streamlit as st

        st.error(f"인터랙티브 패널을 표시하는 중 오류가 발생했습니다: {exc}")
        return False
    return True
