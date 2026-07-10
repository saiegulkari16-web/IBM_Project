# =============================================================
# frontend/daily_brief.py
# Daily Brief page for Money Matters.
#
# Full-page news feed with:
#   • Refresh button
#   • AI-summarised articles
#   • Source + timestamp
#   • Read More links
# =============================================================

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from backend.session import get_daily_brief, set_daily_brief, set_ui_mode
from frontend.components import (
    section_header,
    news_card,
    empty_state,
    divider,
)
from frontend.styles import COLORS
from utils.formatters import format_date


def render_daily_brief() -> None:
    """Render the Daily Brief page."""

    col_home, col_title, col_btn = st.columns([1.2, 5, 1])
    with col_home:
        st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
        if st.button("Home", key="brief_back_home", use_container_width=True):
            set_ui_mode("home")
            st.rerun()
    with col_title:
        section_header(
            "📰 Daily Brief",
            f"Today · {format_date(datetime.now(timezone.utc))}",
        )
    with col_btn:
        st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="brief_refresh"):
            set_daily_brief(None)   # invalidate cache
            st.rerun()

    divider()

    brief = get_daily_brief()

    # Auto-fetch if not cached or stale
    if brief is None or brief.is_stale:
        with st.spinner("Fetching latest financial news..."):
            try:
                from services.news_service import fetch_daily_brief
                brief = fetch_daily_brief(max_articles=8, add_ai_summary=True)
                set_daily_brief(brief)
            except Exception as exc:
                st.error(f"Failed to fetch news: {exc}")
                return

    if not brief or not brief.articles:
        empty_state(
            "📰",
            "No news available",
            "Check your internet connection or try refreshing.",
        )
        return

    # Render articles in a 2-column grid
    articles = brief.articles
    left_col, right_col = st.columns(2)

    for i, article in enumerate(articles):
        col = left_col if i % 2 == 0 else right_col
        with col:
            news_card(article)
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    divider()
    st.markdown(
        f"""
        <p style="text-align:center;font-size:12px;color:{COLORS['text_muted']};">
            Sources: RBI, SEBI, PIB, RSS feeds · Updates daily
        </p>
        """,
        unsafe_allow_html=True,
    )


__all__ = ["render_daily_brief"]
