from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

import streamlit as st

from ..content_loader import load_index
from ..data import CATEGORIES
from .registry import page

CONTENT_DIR = Path("content")
INDEX_PATH = CONTENT_DIR / "index.json"

DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "changeme"


@page(
    "admin",
    title="콘텐츠 관리",
    description="콘텐츠 수정 및 저장",
    icon="🛠️",
)
def render(_: dict | None = None) -> None:
    _ensure_session_defaults()
    if not st.session_state.get("is_admin_authenticated"):
        _render_login()
        return

    st.title("콘텐츠 관리 도구")
    st.caption("예시 인증 로직입니다. 실제 운영 환경에서는 별도의 인증 게이트웨이를 권장합니다.")

    if st.button("로그아웃", type="secondary"):
        st.session_state.is_admin_authenticated = False
        _trigger_rerun()

    items = load_index()
    lookup = {item["id"]: item for item in items}
    if not items:
        st.info("관리할 콘텐츠가 없습니다. index.json을 먼저 확인하세요.")
        return

    col_select, col_new = st.columns([3, 1])
    with col_select:
        selected_id = st.selectbox(
            "콘텐츠 선택",
            options=list(lookup.keys()),
            format_func=lambda key: f"{lookup[key]['title']} ({key})",
        )
    with col_new:
        st.caption("새 항목 추가는 추후 확장하세요.")

    item = lookup[selected_id]

    st.subheader("기본 정보")
    title = st.text_input("제목", value=item.get("title", ""))
    category_keys = [k for k, _ in CATEGORIES]
    try:
        default_category_index = category_keys.index(item.get("category", "all"))
    except ValueError:
        default_category_index = 0
    category = st.selectbox(
        "카테고리",
        options=category_keys,
        format_func=lambda key: next((label for k, label in CATEGORIES if k == key), key),
        index=default_category_index,
    )
    img = st.text_input("이미지 URL", value=item.get("img", ""))
    body_path = st.text_input("본문 파일명", value=item.get("body", ""))

    st.subheader("본문 (Markdown)")
    body_text = _read_body(body_path)
    edited_body = st.text_area("콘텐츠", value=body_text, height=360)

    if st.button("저장", type="primary"):
        _save_changes(
            items,
            selected_id,
            {
                "title": title,
                "category": category,
                "img": img,
                "body": body_path,
            },
            edited_body,
        )
        st.success("저장되었습니다. 페이지를 새로고침하거나 다른 화면에서 확인하세요.")


def _ensure_session_defaults() -> None:
    if "is_admin_authenticated" not in st.session_state:
        st.session_state.is_admin_authenticated = False


def _render_login() -> None:
    st.title("관리자 로그인")
    st.caption("실제 서비스에서는 HTTPS 연결과 외부 인증 시스템을 이용하세요.")

    with st.form("admin-login", clear_on_submit=False):
        user = st.text_input("ID", value="", key="admin-user")
        password = st.text_input("Password", value="", type="password", key="admin-pass")
        submitted = st.form_submit_button("로그인")

    if submitted:
        if _verify_credentials(user, password):
            st.session_state.is_admin_authenticated = True
            st.success("인증에 성공했습니다.")
            _trigger_rerun()
        else:
            st.error("인증에 실패했습니다. ID/PW를 확인하세요.")


def _verify_credentials(user: str, password: str) -> bool:
    valid_user = os.environ.get("EDA_ADMIN_USER", DEFAULT_ADMIN_USER)
    valid_password = os.environ.get("EDA_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    return user == valid_user and password == valid_password


def _read_body(body_path: str) -> str:
    if not body_path:
        return ""
    path = CONTENT_DIR / body_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _save_changes(
    items: List[Dict],
    target_id: str,
    updates: Dict[str, str],
    body_text: str,
) -> None:
    for item in items:
        if item.get("id") == target_id:
            item.update(updates)
            break
    INDEX_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    body_path = updates.get("body")
    if body_path:
        (CONTENT_DIR / body_path).write_text(body_text, encoding="utf-8")


def _trigger_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()
