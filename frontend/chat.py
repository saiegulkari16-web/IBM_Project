# =============================================================
# frontend/chat.py
# Full chat page for Money Matters.
#
# Flow:
#   1. Render existing messages from current conversation
#   2. Accept new user input (chat_input + PDF upload)
#   3. Route via agents/router.route()
#   4. Dispatch to agents/tools.dispatch()
#   5. Stream response, update session + persist history
#   6. Auto-generate conversation title on first message
# =============================================================

from __future__ import annotations

import streamlit as st

from agents.router import route
from agents.tools import dispatch
from backend.models import ChatMessage, MessageRole, IntentType
from backend.session import (
    get_current_conversation,
    add_message_to_current,
    get_current_user,
    is_authenticated,
    get_pdf_context,
    set_pdf_context,
    clear_pdf_context,
    new_conversation,
    set_ui_mode,
    pop_toast,
)
from backend.history import save_conversation, update_conversation_title
from frontend.components import intent_badge, source_tags, empty_state
from frontend.styles import COLORS
from rag.loader import extract_pdf_text
from utils.logger import logger
from utils.validators import validate_chat_input, validate_pdf_file


# ── History → Granite format ──────────────────────────────────

def _build_history(messages: list[ChatMessage]) -> list[dict]:
    """Convert ChatMessage list to role/content dicts for Granite."""
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages[-16:]   # last 16 messages (~8 turns)
        if msg.role in ("user", "assistant")
    ]


# ── Title generator ────────────────────────────────────────────

def _auto_title(first_message: str) -> str:
    """Generate a short conversation title using Granite."""
    try:
        from services.watsonx_service import generate_short
        from utils.prompts import build_title_prompt
        title = generate_short(build_title_prompt(first_message), max_tokens=20)
        return title.strip()[:60] if title else first_message[:50]
    except Exception:
        return first_message[:50]


# ── PDF upload handler ────────────────────────────────────────

def _handle_pdf_upload() -> None:
    """Render the PDF upload widget and extract text into session."""
    uploaded = st.file_uploader(
        "Attach a PDF document",
        type     = ["pdf"],
        key      = "pdf_uploader",
        label_visibility="collapsed",
    )
    if uploaded:
        ok, err = validate_pdf_file(uploaded.name, uploaded.size)
        if not ok:
            st.error(err)
            return
        with st.spinner("Reading PDF..."):
            text = extract_pdf_text(uploaded.read(), uploaded.name)
        if text:
            set_pdf_context(text)
            st.success(f"📎 **{uploaded.name}** attached ({len(text):,} chars). "
                       f"Ask me anything about it!")
        else:
            st.error("Could not extract text from this PDF.")


# ── Message renderer ──────────────────────────────────────────

def _render_messages(messages: list[ChatMessage]) -> None:
    """Render all existing chat messages."""
    for msg in messages:
        role     = msg.role
        avatar   = "user" if role == "user" else "assistant"
        with st.chat_message(avatar):
            st.markdown(msg.content)
            # Show intent badge + sources on assistant messages
            if role == "assistant":
                if msg.intent and msg.intent != "normal_chat":
                    from agents.intents import get_intent_label
                    intent_badge(msg.intent, get_intent_label(msg.intent))
                if msg.sources:
                    source_tags(msg.sources)


# ── Main render ────────────────────────────────────────────────

def render_chat() -> None:
    """Render the chat page."""

    # Pop any queued toast
    toast = pop_toast()
    if toast:
        st.toast(f"{toast[1]} {toast[0]}")

    conv = get_current_conversation()
    user = get_current_user()

    if conv is None:
        empty_state(
            "💬",
            "No conversation selected",
            "Click + New Chat in the sidebar to start.",
        )
        if st.button("+ New Chat", key="chat_empty_new", type="primary"):
            new_conversation()
            st.rerun()
        return

    nav_col, _ = st.columns([1.2, 8], gap="small")
    with nav_col:
        if st.button("Home", key="chat_back_home", use_container_width=True):
            set_ui_mode("home")
            st.rerun()

    # ── PDF upload toggle ──────────────────────────────────
    show_pdf = st.session_state.get("trigger_pdf_upload", False)
    if show_pdf:
        _handle_pdf_upload()
        st.session_state["trigger_pdf_upload"] = False

    # Show active PDF badge
    pdf_text = get_pdf_context()
    if pdf_text:
        col1, col2 = st.columns([8, 1])
        with col1:
            st.info("📎 PDF attached — questions will reference this document.")
        with col2:
            if st.button("✕", key="remove_pdf", help="Remove attached PDF"):
                clear_pdf_context()
                st.rerun()

    # ── Conversation title bar ────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:8px;
                    padding:0.5rem 0 1rem;">
            <span style="font-size:15px;font-weight:600;
                         color:{COLORS['text']};">
                {conv.title}
            </span>
            <span style="font-size:11px;color:{COLORS['text_muted']};">
                · {conv.message_count} message{"s" if conv.message_count != 1 else ""}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Message history ────────────────────────────────────
    _render_messages(conv.messages)

    # ── Handle pending message from home page ─────────────
    pending_msg    = st.session_state.pop("pending_message", None)
    pending_intent = st.session_state.pop("pending_intent", None)

    # ── Chat input ─────────────────────────────────────────
    # Button row above input
    btn_cols = st.columns([1, 1, 1, 1, 6])
    with btn_cols[0]:
        if st.button("🔬", key="chat_dd",  help="Deep Dive"):
            pending_intent = IntentType.DEEP_DIVE
    with btn_cols[1]:
        if st.button("🌐", key="chat_sw",  help="Search Web"):
            pending_intent = IntentType.WEB_SEARCH
    with btn_cols[2]:
        if st.button("📎", key="chat_pdf", help="Attach PDF"):
            st.session_state["trigger_pdf_upload"] = True
            st.rerun()
    with btn_cols[3]:
        if st.button("🧮", key="chat_calc", help="Calculator"):
            set_ui_mode("calculator")
            st.rerun()

    user_input = st.chat_input(
        "Ask anything about finance...",
        key="chat_main_input",
    )

    # Merge pending or new input
    final_input  = pending_msg or user_input
    final_intent = pending_intent

    if not final_input:
        return

    # ── Validate ───────────────────────────────────────────
    ok, err = validate_chat_input(final_input)
    if not ok:
        st.error(err)
        return

    # ── Add user message ───────────────────────────────────
    user_msg = ChatMessage(
        role    = MessageRole.USER,
        content = final_input,
        intent  = final_intent,
    )
    add_message_to_current(user_msg)

    with st.chat_message("user"):
        st.markdown(final_input)

    # ── Route + Dispatch ──────────────────────────────────
    with st.chat_message("assistant"):
        history  = _build_history(conv.messages[:-1])   # exclude just-added user msg
        decision = route(
            message         = final_input,
            override_intent = final_intent,
        )

        try:
            result = dispatch(
                decision=decision,
                history=history,
                pdf_text=get_pdf_context(),
                stream=False,
            )
            full_text = (result.text or "").strip() or "I'm here. I couldn't generate a full reply right now, but please try again."
            st.markdown(full_text)
        except Exception as exc:
            logger.error("Chat response failed: {}", exc)
            result = None
            full_text = "I'm here, but something went wrong while generating a response. Please try again."
            st.markdown(full_text)

        # Show intent badge + sources
        if decision.intent != IntentType.NORMAL_CHAT:
            from agents.intents import get_intent_label
            intent_badge(decision.intent, get_intent_label(decision.intent))
        if result and result.sources:
            source_tags(result.sources)

    # ── Save assistant message ─────────────────────────────
    ai_msg = ChatMessage(
        role    = MessageRole.ASSISTANT,
        content = full_text,
        intent  = decision.intent,
        sources = result.sources if result else [],
    )
    add_message_to_current(ai_msg)

    # Auto-title on first exchange
    if conv.message_count == 2 and conv.title == "New Conversation":
        title = _auto_title(final_input)
        conv.title = title
        if user and is_authenticated():
            update_conversation_title(user.id, conv.id, title)

    # Persist to disk
    if user and is_authenticated():
        save_conversation(user.id, conv)

    st.rerun()


__all__ = ["render_chat"]
