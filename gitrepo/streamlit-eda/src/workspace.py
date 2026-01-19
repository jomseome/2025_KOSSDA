from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st
from markdown import markdown as md_to_html

try:
    from streamlit_quill import st_quill

    HAS_QUILL = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_QUILL = False

from .generated_content import ensure_unique_slug, list_stories, load_story, save_story
from .markdown_utils import auto_format_text
from .visual_runtime import render_visual_from_registry


def _state_key(slug: str, suffix: str) -> str:
    return f"admin_{slug}_{suffix}"


def _append_to_markdown(story_slug: str, key: str, snippet: str) -> None:
    base = st.session_state.get(key, "") or ""
    st.session_state[key] = base + snippet


def _ensure_story_state(slug: str) -> None:
    story = load_story(slug) or {}

    title_key = _state_key(slug, "title")
    st.session_state.setdefault(title_key, story.get("title", ""))

    markdown_key = _state_key(slug, "markdown")
    st.session_state.setdefault(markdown_key, story.get("markdown", ""))

    format_key = _state_key(slug, "format")
    st.session_state.setdefault(format_key, story.get("format", "markdown"))

    source_key = _state_key(slug, "source")
    st.session_state.setdefault(source_key, story.get("pdf_source", ""))

    slots_key = _state_key(slug, "visual_slots")
    slot_data_key = _state_key(slug, "visual_slot_data")
    if slots_key not in st.session_state:
        slots: List[str] = []
        slot_data: Dict[str, Dict[str, Any]] = {}
        visuals = story.get("visuals") or {}
        if isinstance(visuals, dict):
            for index, (slot_id, payload) in enumerate(visuals.items(), start=1):
                key_id = slot_id if isinstance(slot_id, str) else f"slot-{index}"
                slots.append(key_id)
                slot_data[key_id] = {
                    "title": payload.get("title") if isinstance(payload, dict) else "",
                    "caption": payload.get("caption") if isinstance(payload, dict) else "",
                    "renderer": payload.get("renderer") if isinstance(payload, dict) else "",
                }
        st.session_state[slots_key] = slots
        st.session_state[slot_data_key] = slot_data

    slots = st.session_state.get(slots_key, [])
    slot_data = st.session_state.get(slot_data_key, {})
    for slot_id in slots:
        slot_state = slot_data.setdefault(slot_id, {"title": "", "caption": "", "renderer": ""})
        st.session_state.setdefault(_state_key(slug, f"{slot_id}_title"), slot_state.get("title", ""))
        st.session_state.setdefault(_state_key(slug, f"{slot_id}_caption"), slot_state.get("caption", ""))
        st.session_state.setdefault(_state_key(slug, f"{slot_id}_renderer"), slot_state.get("renderer", ""))


def _add_visual_slot(slug: str) -> str:
    slots_key = _state_key(slug, "visual_slots")
    slot_data_key = _state_key(slug, "visual_slot_data")
    slots: List[str] = st.session_state.setdefault(slots_key, [])
    slot_data: Dict[str, Dict[str, Any]] = st.session_state.setdefault(slot_data_key, {})

    counter = 1
    while True:
        candidate = f"slot-{counter}"
        if candidate not in slots:
            slots.append(candidate)
            slot_data[candidate] = {"title": "", "caption": "", "renderer": ""}
            st.session_state[_state_key(slug, f"{candidate}_title")] = ""
            st.session_state[_state_key(slug, f"{candidate}_caption")] = ""
            st.session_state[_state_key(slug, f"{candidate}_renderer")] = ""
            return candidate
        counter += 1


def _remove_visual_slot(slug: str, slot_id: str) -> None:
    slots_key = _state_key(slug, "visual_slots")
    slot_data_key = _state_key(slug, "visual_slot_data")
    slots: List[str] = st.session_state.get(slots_key, [])
    slot_data: Dict[str, Dict[str, Any]] = st.session_state.get(slot_data_key, {})
    if slot_id in slots:
        slots.remove(slot_id)
    slot_data.pop(slot_id, None)
    for suffix in ("title", "caption", "renderer"):
        st.session_state.pop(_state_key(slug, f"{slot_id}_{suffix}"), None)


def _render_story_editor(slug: str) -> None:
    _ensure_story_state(slug)

    title_key = _state_key(slug, "title")
    markdown_key = _state_key(slug, "markdown")
    format_key = _state_key(slug, "format")
    source_key = _state_key(slug, "source")
    slots_key = _state_key(slug, "visual_slots")
    slot_data_key = _state_key(slug, "visual_slot_data")

    st.subheader("기본 정보")
    st.text_input("스토리 제목", key=title_key, placeholder="제목을 입력하세요.")
    st.text_input("데이터/출처(선택)", key=source_key, placeholder="예) 통계청, 연구 보고서 등")

    tabs = st.tabs(["본문 작성", "시각화 슬롯", "미리보기"])

    # 본문 작성
    with tabs[0]:
        st.caption("필요한 위치에 `{{viz:slot-1}}` 형태의 토큰을 삽입하면 해당 위치에 시각화를 렌더링합니다.")
        slot_options = st.session_state.get(slots_key, [])
        if slot_options:
            insert_col1, insert_col2 = st.columns([2, 1])
            selected_slot = insert_col1.selectbox(
                "삽입할 시각화 슬롯",
                options=slot_options,
                key=_state_key(slug, "selected_insert_slot"),
            )
            insert_col2.button(
                "토큰 삽입",
                key=_state_key(slug, "insert_slot_token"),
                on_click=_append_to_markdown,
                kwargs={
                    "story_slug": slug,
                    "key": markdown_key,
                    "snippet": f"\n\n{{viz:{selected_slot}}}\n\n",
                },
            )
        else:
            st.info("시각화 슬롯을 추가하면 토큰을 삽입할 수 있습니다.")
            if st.button("기본 슬롯 추가 및 토큰 삽입", key=_state_key(slug, "auto_add_and_insert")):
                new_slot = _add_visual_slot(slug)
                _append_to_markdown(
                    slug,
                    markdown_key,
                    f"\n\n{{viz:{new_slot}}}\n\n",
                )
                st.experimental_rerun()

        if HAS_QUILL:
            st.caption("Quill 편집기를 사용 중입니다. 하단에서 PDF 텍스트 자동 정리 기능을 활용할 수 있습니다.")
            current_content = st.session_state.get(markdown_key, "")
            html_content = (
                current_content
                if st.session_state.get(format_key) == "html"
                else md_to_html(current_content, extensions=["tables", "fenced_code"])
            )
            st.session_state[markdown_key] = html_content
            st.session_state[format_key] = "html"
            new_value = st_quill(
                value=html_content,
                html=True,
                key=_state_key(slug, "quill_editor"),
                placeholder="본문을 작성하세요.",
            )
            if new_value is not None:
                st.session_state[markdown_key] = new_value
        else:
            st.session_state[format_key] = "markdown"
            st.text_area(
                "마크다운 본문",
                key=markdown_key,
                height=420,
                placeholder="본문을 마크다운 형식으로 작성하세요.",
            )

        with st.expander("본문 자동 정리", expanded=False):
            if st.button("본문 자동 정리", key=_state_key(slug, "auto_format_markdown")):
                formatted = auto_format_text(st.session_state.get(markdown_key, ""))
                if formatted:
                    st.session_state[markdown_key] = formatted
                    st.info("본문을 정리했습니다.")
                else:
                    st.info("정리할 내용이 없습니다.")

    # 시각화 슬롯 관리
    with tabs[1]:
        slots = st.session_state.get(slots_key, [])
        slot_data = st.session_state.get(slot_data_key, {})

        st.button("시각화 슬롯 추가", key=_state_key(slug, "add_visual_slot_btn"), on_click=_add_visual_slot, args=(slug,))

        if not slots:
            st.info("아직 등록된 시각화 슬롯이 없습니다. 버튼을 눌러 공란을 추가하세요.")
        else:
            st.info("렌더러 함수는 `src/custom_visuals.py`에 정의해야 합니다. 스토리와 슬롯 ID를 기반으로 Plotly Figure를 반환하도록 구현하세요.")
            for slot_id in slots:
                title_key = _state_key(slug, f"{slot_id}_title")
                caption_key = _state_key(slug, f"{slot_id}_caption")
                renderer_key = _state_key(slug, f"{slot_id}_renderer")
                st.session_state.setdefault(renderer_key, slot_data.get(slot_id, {}).get("renderer", ""))

                with st.expander(f"슬롯 {slot_id}", expanded=True):
                    st.text_input("표시 제목 (선택)", key=title_key, placeholder="본문에 함께 보여줄 제목")
                    st.text_input("캡션 (선택)", key=caption_key, placeholder="시각화 하단에 표시할 설명")
                    st.text_input(
                        "렌더러 함수 이름",
                        key=renderer_key,
                        placeholder="예) covid_section2_chart",
                        help="Python 코드에서 Plotly Figure를 반환하는 함수 이름을 입력하세요.",
                    )
                    if st.button("슬롯 삭제", key=_state_key(slug, f"remove_{slot_id}")):
                        _remove_visual_slot(slug, slot_id)
                        st.experimental_rerun()

    # 미리보기
    with tabs[2]:
        markdown_text = st.session_state.get(markdown_key, "")
        content_format = st.session_state.get(format_key, "markdown")
        slots = st.session_state.get(slots_key, [])
        slot_data = st.session_state.get(slot_data_key, {})

        visual_entries: Dict[str, Dict[str, Any]] = {}
        for slot_id in slots:
            title_value = st.session_state.get(_state_key(slug, f"{slot_id}_title"), "")
            caption_value = st.session_state.get(_state_key(slug, f"{slot_id}_caption"), "")
            renderer_name = st.session_state.get(_state_key(slug, f"{slot_id}_renderer"), "")
            visual_entries[slot_id] = {
                "renderer": renderer_name,
                "figure": None,
                "error": None,
                "title": title_value,
                "caption": caption_value,
            }

        default_slot = next(iter(slots), None)

        def _renderer(slot_id: Optional[str]) -> Optional[bool]:
            target = slot_id or default_slot
            if not target:
                st.info("시각화 슬롯이 설정되지 않았습니다.")
                return False
            entry = visual_entries.get(target)
            if not entry:
                st.info(f"시각화 슬롯 `{target}` 정보를 찾을 수 없습니다.")
                return False
            renderer_name = entry.get("renderer", "").strip()
            if not renderer_name:
                st.info(f"`{target}` 슬롯에 연결된 렌더러가 없습니다. 함수 이름을 설정해 주세요.")
                return False
            title_value = entry.get("title")
            if title_value:
                st.markdown(f"<div class='story-content'><h4>{title_value}</h4></div>", unsafe_allow_html=True)
            fig, error = render_visual_from_registry(renderer_name, slug, target)
            if error:
                st.warning(f"렌더러 실행 오류: {error}")
                return False
            caption_value = entry.get("caption")
            st.plotly_chart(fig, use_container_width=True, key=f"preview_render_{slug}_{target}")
            if caption_value:
                st.caption(caption_value)
            return True

        render_story_content(
            markdown_text,
            content_format=content_format,
            chart_renderer=_renderer if visual_entries else None,
        )

        st.divider()
        if st.button("스토리 저장", type="primary", key=_state_key(slug, "save_story")):
            if not st.session_state.get(title_key, "").strip():
                st.error("스토리 제목을 입력하세요.")
            else:
                slots = st.session_state.get(slots_key, [])
                slot_payload: Dict[str, Dict[str, Any]] = {}
                for slot_id in slots:
                    renderer_value = st.session_state.get(_state_key(slug, f"{slot_id}_renderer"), "").strip()
                    title_value = st.session_state.get(_state_key(slug, f"{slot_id}_title"), "").strip()
                    caption_value = st.session_state.get(_state_key(slug, f"{slot_id}_caption"), "").strip()
                    slot_payload[slot_id] = {
                        "renderer": renderer_value or None,
                        "title": title_value or None,
                        "caption": caption_value or None,
                    }

                payload: Dict[str, Any] = {
                    "title": st.session_state.get(title_key, "").strip() or "데이터 스토리",
                    "markdown": markdown_text,
                    "format": content_format,
                    "pdf_source": st.session_state.get(source_key) or None,
                }
                if slot_payload:
                    payload["visuals"] = slot_payload
                save_story(slug, payload)
                st.success("스토리를 저장했습니다. 사용자 페이지에서 확인해 주세요.")


def render_workspace(*, admin_mode: bool = False) -> None:
    if not admin_mode:
        st.warning("이 워크스페이스는 관리자 전용입니다.")
        return

    st.title("데이터 스토리 관리자")
    st.caption("본문과 시각화 코드를 함께 관리할 수 있는 환경입니다.")

    stories = list_stories()
    story_slugs = list(stories.keys())

    with st.sidebar:
        st.header("스토리 목록")
        selected_slug: Optional[str] = None
        if story_slugs:
            selected_slug = st.radio(
                "편집할 스토리",
                options=story_slugs,
                format_func=lambda slug: stories.get(slug, slug),
                key="workspace_story_select",
            )
        else:
            st.info("등록된 스토리가 없습니다. 새 스토리를 추가하세요.")

        st.subheader("새 스토리 추가")
        new_title = st.text_input("스토리 제목", key="workspace_new_story_title")
        if st.button("추가", key="workspace_add_story"):
            slug = ensure_unique_slug(new_title or "새 스토리")
            save_story(
                slug,
                {
                    "title": new_title or "새 스토리",
                    "markdown": "",
                    "format": "markdown",
                    "visuals": {},
                },
            )
            st.success(f"새 스토리 `{slug}`를 추가했습니다.")
            st.experimental_rerun()

    if not story_slugs:
        return

    selected_slug = selected_slug or story_slugs[0]
    st.write("")
    st.markdown(f"### 현재 편집 중: `{selected_slug}`")

    _render_story_editor(selected_slug)
