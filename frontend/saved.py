# =============================================================
# frontend/saved.py
# Saved Conversations page for Money Matters.
#
# Features:
#   • Lists all non-deleted conversations for the logged-in user
#   • Search bar to filter by title / content
#   • Open, pin/unpin, export as Markdown, delete
#   • Guest users see an invitation to sign in
# =============================================================

from __future__ import annotations

import streamlit as st

from backend.history import (
    get_recent_conversations,
    search_conversations,
    delete_conversation,
    toggle_pin,
    export_conversation_markdown,
    load_conversation,
)
from backend.session import (
    get_current_user,
    is_authenticated,
    set_current_conversation,
    set_ui_mode,
)
from frontend.components import (
    section_header,
    empty_state,
    divider,
)
from frontend.styles import COLORS
from utils.formatters import format_datetime, relative_time


def render_saved() -> None:
    """Render the Saved Conversations page."""

    section_header("🔖 Saved Conversations", "Your financial literacy journey")
    divider()

    user = get_current_user()

    if not is_authenticated() or not user:
        empty_state(
            "🔒",
            "Sign in to view saved conversations",
            "Your conversations are saved automatically when you're logged in.",
        )
        if st.button("Sign In →", key="saved_signin", type="primary"):
            set_ui_mode("login")
            st.rerun()
        return

    # ── Search bar ────────────────────────────────────────
    query = st.text_input(
        "Search conversations",
        placeholder="Search by topic, keyword...",
        key          = "saved_search",
        label_visibility="collapsed",
    )

    # ── Load conversations ────────────────────────────────
    if query.strip():
        conversations = search_conversations(user.id, query)
    else:
        conversations = get_recent_conversations(user.id, limit=50)

    if not conversations:
        if query:
            empty_state(
                "🔍",
                f"No results for '{query}'",
                "Try different keywords.",
            )
        else:
            empty_state(
                "💬",
                "No conversations yet",
                "Start chatting and your history will appear here.",
            )
        return

    # ── Conversation list ─────────────────────────────────
    st.markdown(
        f"""
        <div style="font-size:12px;color:{COLORS['text_muted']};
                    margin-bottom:0.75rem;">
            {len(conversations)} conversation{"s" if len(conversations) != 1 else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    for conv in conversations:
        _render_conv_row(conv, user.id)


def _render_conv_row(conv, user_id: str) -> None:
    """Render a single conversation row with actions."""
    pin_icon = "📌" if conv.pinned else "📄"
    time_str = relative_time(conv.updated_at) if conv.updated_at else ""
    preview  = conv.last_message_preview

    with st.container():
        st.markdown(
            f"""
            <div class="mm-card" style="margin-bottom:0.6rem;">
                <div style="display:flex;align-items:flex-start;
                            justify-content:space-between;gap:1rem;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:14px;font-weight:600;
                                    color:{COLORS['text']};margin-bottom:3px;
                                    white-space:nowrap;overflow:hidden;
                                    text-overflow:ellipsis;">
                            {pin_icon} {conv.title}
                        </div>
                        <div style="font-size:12px;color:{COLORS['text_muted']};">
                            {time_str} · {conv.message_count} messages
                        </div>
                        <div style="font-size:13px;color:{COLORS['text_muted']};
                                    margin-top:3px;white-space:nowrap;
                                    overflow:hidden;text-overflow:ellipsis;">
                            {preview}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_cols = st.columns([2, 1, 1, 1, 1])

        with btn_cols[0]:
            if st.button("Open", key=f"open_{conv.id}", use_container_width=True,
                         type="primary"):
                convs = st.session_state.get("conversations", {})
                if conv.id not in convs:
                    loaded = load_conversation(user_id, conv.id)
                    if loaded:
                        convs[conv.id] = loaded
                        st.session_state["conversations"] = convs
                set_current_conversation(conv.id)
                st.rerun()

        with btn_cols[1]:
            pin_label = "Unpin" if conv.pinned else "Pin"
            if st.button(pin_label, key=f"pin_{conv.id}", use_container_width=True):
                toggle_pin(user_id, conv.id)
                st.rerun()

        with btn_cols[2]:
            if st.button("Export", key=f"export_{conv.id}", use_container_width=True):
                loaded = load_conversation(user_id, conv.id)
                if loaded:
                    md_content = export_conversation_markdown(loaded)
                    st.download_button(
                        "Download .md",
                        data          = md_content,
                        file_name     = f"{conv.title[:40]}.md",
                        mime          = "text/markdown",
                        key           = f"dl_{conv.id}",
                    )

        with btn_cols[3]:
            if st.button("Delete", key=f"del_{conv.id}", use_container_width=True):
                delete_conversation(user_id, conv.id, soft=True)
                # Remove from session state too
                convs = st.session_state.get("conversations", {})
                convs.pop(conv.id, None)
                st.rerun()


__all__ = ["render_saved"]
