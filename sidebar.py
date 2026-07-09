from __future__ import annotations

import streamlit as st

from backend.history import get_recent_conversations
from backend.session import (
    get_current_user,
    get_ui_mode,
    is_authenticated,
    logout_user,
    new_conversation,
    set_current_conversation,
    set_ui_mode,
)
from frontend.components import render_logo
from utils.formatters import relative_time, truncate_text


def _nav_button(label: str, mode: str, icon: str, badge: str = "") -> None:
    active = get_ui_mode() == mode
    button_label = f"{icon}  {label}"
    if st.button(
        button_label,
        key=f"nav_{mode}",
        use_container_width=True,
        type="primary" if active else "secondary",
    ):
        set_ui_mode(mode)
        st.rerun()

    if badge:
        st.markdown(
            f'<div class="mm-nav-badge-row"><span>{badge}</span></div>',
            unsafe_allow_html=True,
        )


def _recent_row(conv) -> None:
    title = truncate_text(conv.title.strip() or "Untitled chat", 26)
    time_label = relative_time(conv.updated_at)

    left, right = st.columns([4.2, 1.3], gap="small")
    with left:
        clicked = st.button(
            f"☑  {title}",
            key=f"conv_{conv.id}",
            use_container_width=True,
        )
    with right:
        st.markdown(
            f'<div class="mm-recent-time">{time_label}</div>',
            unsafe_allow_html=True,
        )

    if clicked:
        convs = st.session_state.get("conversations", {})
        convs[conv.id] = conv
        st.session_state["conversations"] = convs
        set_current_conversation(conv.id)
        st.rerun()


def _render_recent() -> None:
    user = get_current_user()
    if not (is_authenticated() and user):
        return

    recent = [conv for conv in get_recent_conversations(user.id, limit=8) if conv.message_count > 0]
    if not recent:
        return

    st.markdown('<div class="mm-sidebar-section-title">Recent</div>', unsafe_allow_html=True)
    for conv in recent:
        _recent_row(conv)


def render_sidebar() -> None:
    """Render the sidebar close to the reference layout."""
    with st.sidebar:
        render_logo()
        st.markdown("<div class='mm-sidebar-spacer'></div>", unsafe_allow_html=True)

        if st.button(
            "＋  New Chat",
            key="btn_new_chat",
            use_container_width=True,
            type="primary",
        ):
            new_conversation()
            st.rerun()

        st.markdown("<div class='mm-sidebar-spacer'></div>", unsafe_allow_html=True)
        _nav_button("Search", "search", "⌕")
        _nav_button("Calculator", "calculator", "◫")
        _nav_button("Daily Brief", "brief", "▤", badge="NEW")

        st.markdown("<div class='mm-sidebar-gap'></div>", unsafe_allow_html=True)
        _render_recent()
        st.markdown("<div class='mm-sidebar-gap'></div>", unsafe_allow_html=True)

        _nav_button("Saved", "saved", "🔖")
        _nav_button("Settings", "settings", "⚙")

        st.markdown("<div class='mm-sidebar-footer-gap'></div>", unsafe_allow_html=True)
        user = get_current_user()
        if is_authenticated() and user:
            st.markdown(
                f"""
                <div class="mm-user-card">
                    <div class="mm-user-name">{user.display_name or user.username}</div>
                    <div class="mm-user-email">{user.email}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Sign Out", key="btn_logout", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            if st.button("Login", key="btn_login", use_container_width=True):
                set_ui_mode("login")
                st.rerun()


__all__ = ["render_sidebar"]
