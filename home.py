from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from backend.history import get_recent_conversations
from backend.models import IntentType
from backend.session import (
    get_current_user,
    get_daily_brief,
    get_ui_mode,
    is_authenticated,
    logout_user,
    new_conversation,
    set_current_conversation,
    set_daily_brief,
    set_ui_mode,
)
from frontend.components import news_card, render_logo, section_header
from frontend.styles import COLORS, inject_css
from utils.formatters import format_date, relative_time, truncate_text


_FEATURE_CARDS = [
    {
        "icon": "Deep Dive",
        "title": "Deep Dive",
        "desc": "Get in-depth analysis on any financial topic.",
        "cta": "Explore",
        "mode": "chat",
        "intent": IntentType.DEEP_DIVE,
    },
    {
        "icon": "Calculator",
        "title": "Calculator",
        "desc": "Calculate SIP, loans, EMI, returns and more.",
        "cta": "Calculate",
        "mode": "calculator",
        "intent": None,
    },
    {
        "icon": "Compare",
        "title": "Compare",
        "desc": "Compare schemes, FDs, loans and more.",
        "cta": "Compare",
        "mode": "chat",
        "intent": IntentType.GOVERNMENT_SCHEME,
    },
    {
        "icon": "Search Web",
        "title": "Search Web",
        "desc": "Search the web for real-time information.",
        "cta": "Search",
        "mode": "chat",
        "intent": IntentType.WEB_SEARCH,
    },
]


def _hide_native_sidebar() -> None:
    inject_css(
        """
        [data-testid="stSidebar"] { display: none !important; }
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
        """
    )


def _top_bar(is_auth: bool, name: str) -> None:
    left, theme_col, login_col = st.columns([7.5, 1, 1.5], gap="medium")
    with left:
        st.markdown("", unsafe_allow_html=True)
    with theme_col:
        st.button("☼", key="theme_btn_home", use_container_width=True)
    with login_col:
        label = name if is_auth else "Login"
        if st.button(label, key="home_login_btn", use_container_width=True, type="primary" if not is_auth else "secondary"):
            if not is_auth:
                set_ui_mode("login")
                st.rerun()


def _custom_sidebar() -> None:
    render_logo()

    if st.button("+  New Chat", key="home_new_chat", use_container_width=True, type="primary"):
        new_conversation()
        st.rerun()

    st.markdown("<div class='mm-home-side-gap'></div>", unsafe_allow_html=True)

    nav_items = [
        ("Search", "search", "⌕"),
        ("Calculator", "calculator", "◫"),
        ("Daily Brief", "brief", "▤"),
        ("Saved", "saved", "🔖"),
        ("Settings", "settings", "⚙"),
    ]
    current_mode = get_ui_mode()
    for label, mode, icon in nav_items:
        if st.button(
            f"{icon}  {label}",
            key=f"home_nav_{mode}",
            use_container_width=True,
            type="primary" if current_mode == mode else "secondary",
        ):
            set_ui_mode(mode)
            st.rerun()

    user = get_current_user()
    if is_authenticated() and user:
        recent = [conv for conv in get_recent_conversations(user.id, limit=8) if conv.message_count > 0]
        if recent:
            st.markdown('<div class="mm-home-recent-title">Recent</div>', unsafe_allow_html=True)
            for conv in recent:
                left, right = st.columns([4, 1.2], gap="small")
                with left:
                    clicked = st.button(
                        f"☑  {truncate_text(conv.title, 24)}",
                        key=f"home_recent_{conv.id}",
                        use_container_width=True,
                    )
                with right:
                    st.markdown(
                        f'<div class="mm-home-recent-time">{relative_time(conv.updated_at)}</div>',
                        unsafe_allow_html=True,
                    )
                if clicked:
                    convs = st.session_state.get("conversations", {})
                    convs[conv.id] = conv
                    st.session_state["conversations"] = convs
                    set_current_conversation(conv.id)
                    st.rerun()

        st.markdown("<div class='mm-home-side-gap'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="mm-user-card">
                <div class="mm-user-name">{user.display_name or user.username}</div>
                <div class="mm-user-email">{user.email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", key="home_sign_out", use_container_width=True):
            logout_user()
            st.rerun()



def _quick_actions() -> None:
    labels = ["Analyze", "Plan", "Invest", "Grow"]
    cols = st.columns(4, gap="small")
    for col, label in zip(cols, labels):
        with col:
            if st.button(label, key=f"quick_{label.lower()}", use_container_width=True):
                new_conversation()
                st.session_state["prefill_message"] = label
                st.rerun()


def _composer() -> None:
    prompt = st.text_input(
        "Ask anything about finance...",
        key="home_prompt_input",
        label_visibility="collapsed",
        placeholder="Ask anything about finance...",
    )
    cols = st.columns([0.9, 1.9, 1.9, 1.9, 0.8, 0.8], gap="small")
    with cols[0]:
        st.button("+", key="home_plus", use_container_width=True)
    with cols[1]:
        deep_dive = st.button("Deep Dive", key="home_dd", use_container_width=True)
    with cols[2]:
        search_web = st.button("Search Web", key="home_sw", use_container_width=True)
    with cols[3]:
        attach_file = st.button("Attach File", key="home_af", use_container_width=True)
    with cols[4]:
        st.button("Mic", key="home_mic", use_container_width=True)
    with cols[5]:
        send = st.button("↑", key="home_send", use_container_width=True, type="primary")

    if send and prompt.strip():
        new_conversation()
        st.session_state["pending_message"] = prompt.strip()
        st.rerun()

    if deep_dive:
        new_conversation()
        st.session_state["pending_intent"] = IntentType.DEEP_DIVE
        st.rerun()

    if search_web:
        new_conversation()
        st.session_state["pending_intent"] = IntentType.WEB_SEARCH
        st.rerun()

    if attach_file:
        new_conversation()
        st.session_state["trigger_pdf_upload"] = True
        st.rerun()


def _trust_badges() -> None:
    badges = [
        ("Trusted Sources", "RBI, SEBI and more"),
        ("Real-time Updates", "Stay ahead daily"),
        ("AI-Powered Insights", "Smart. Fast. Reliable."),
    ]
    cols = st.columns(3, gap="medium")
    for col, (title, subtitle) in zip(cols, badges):
        with col:
            st.markdown(
                f"""
                <div class="mm-soft-card mm-badge-card">
                    <div class="mm-badge-title">{title}</div>
                    <div class="mm-badge-subtitle">{subtitle}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _feature_cards() -> None:
    section_header(
        "Explore Smart Tools",
        "Everything you need to make better financial decisions",
    )
    cols = st.columns(4, gap="medium")
    for col, card in zip(cols, _FEATURE_CARDS):
        with col:
            st.markdown(
                f"""
                <div class="mm-feature-card">
                    <span class="icon">{card['icon']}</span>
                    <h4>{card['title']}</h4>
                    <p>{card['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"{card['cta']} ->",
                key=f"feature_{card['title'].lower().replace(' ', '_')}",
                use_container_width=True,
            ):
                if card["mode"] == "calculator":
                    set_ui_mode("calculator")
                else:
                    new_conversation()
                    if card["intent"]:
                        st.session_state["pending_intent"] = card["intent"]
                st.rerun()


def _bottom_banner() -> None:
    st.markdown(
        """
        <div class="mm-hero-banner">
            <div class="mm-hero-copy">
                <div class="mm-hero-title">Smart today, secure tomorrow.</div>
                <div class="mm-hero-subtitle">Make informed financial decisions with Money Matters.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _daily_brief_panel() -> None:
    today_str = format_date(datetime.now(timezone.utc))
    brief = get_daily_brief()
    attempted = st.session_state.get("daily_brief_attempted", False)

    if brief is None and not attempted:
        with st.spinner("Fetching latest news..."):
            try:
                from services.news_service import fetch_daily_brief

                brief = fetch_daily_brief(max_articles=3, add_ai_summary=False)
                set_daily_brief(brief)
            except Exception:
                brief = None
            finally:
                st.session_state["daily_brief_attempted"] = True

    st.markdown(
        f"""
        <div class="mm-brief-hero">
            <div>
                <div class="mm-brief-kicker">Daily Brief</div>
                <div class="mm-brief-date">Today · {today_str}</div>
            </div>
        </div>
        <div class="mm-brief-heading">
            <span>Top Financial News</span>
            <span>View All -></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if brief and brief.articles:
        for article in brief.articles[:3]:
            news_card(article)
    else:
        st.markdown(
            f"""
            <div style="padding:1rem 0;color:{COLORS['text_muted']};font-size:13px;">
                No news available right now. Check back later.
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Go to Daily Brief ->", key="home_daily_brief_btn", use_container_width=True, type="primary"):
        set_ui_mode("brief")
        st.rerun()


def render_home() -> None:
    """Render the dashboard to match the reference image more closely."""
    _hide_native_sidebar()

    user = get_current_user()
    is_auth = is_authenticated()
    name = user.first_name if user else "User"

    left_col, main_col, right_col = st.columns([1.0, 2.7, 1.15], gap="large")

    with left_col:
        _custom_sidebar()

    with main_col:
        _top_bar(is_auth, name)
        st.markdown(
            f"""
            <div class="mm-welcome">
                <h1>Welcome, <span>{name}</span>!</h1>
                <p>Your AI copilot for smarter financial decisions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _quick_actions()
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        _composer()
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        _trust_badges()
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        _feature_cards()
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        _bottom_banner()

    with right_col:
        _daily_brief_panel()


__all__ = ["render_home"]
