# =============================================================
# frontend/app.py
# Money Matters — Streamlit Application Entry Point
#
# Usage:
#   streamlit run frontend/app.py
#
# This file:
#   1. Configures the Streamlit page
#   2. Applies the CSS theme
#   3. Initialises session state
#   4. Renders the sidebar
#   5. Routes to the correct page based on ui_mode
# =============================================================

from __future__ import annotations

import sys
from pathlib import Path

# ── Ensure project root is on sys.path ───────────────────────
# Allows `from backend.models import ...` etc. from any working directory
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

# ── Page config — must be first Streamlit call ───────────────
st.set_page_config(
    page_title     = "Money Matters",
    page_icon      = "💰",
    layout         = "wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Money Matters — AI-powered Financial Literacy Assistant. IBM SkillsBuild 2025.",
    },
)

# ── Imports after set_page_config ────────────────────────────
from frontend.styles     import apply_theme
from frontend.sidebar    import render_sidebar
from frontend.home       import render_home
from frontend.chat       import render_chat
from frontend.auth       import render_auth_page
from frontend.calculator import render_calculator
from frontend.daily_brief import render_daily_brief
from frontend.saved      import render_saved
from frontend.settings   import render_settings
from frontend.components import show_toast
from backend.session import (
    init_session,
    get_ui_mode,
    set_ui_mode,
    pop_toast,
)


# ── Apply theme ───────────────────────────────────────────────
apply_theme()


# ── Initialise session state ─────────────────────────────────
init_session()


# ── Toast notifications ───────────────────────────────────────
toast = pop_toast()
if toast:
    st.toast(f"{toast[1]} {toast[0]}")


# ── Sidebar ───────────────────────────────────────────────────
render_sidebar()


# ── Page routing ─────────────────────────────────────────────
mode = get_ui_mode()

if mode == "home":
    render_home()

elif mode == "chat":
    render_chat()

elif mode == "login":
    render_auth_page()

elif mode == "calculator":
    render_calculator()

elif mode == "brief":
    render_daily_brief()

elif mode == "saved":
    render_saved()

elif mode == "settings":
    render_settings()

elif mode == "search":
    # Search is handled inline via the chat page with web_search intent
    set_ui_mode("chat")
    st.session_state["pending_intent"] = "web_search"
    st.rerun()

else:
    # Unknown mode — fallback to home
    set_ui_mode("home")
    st.rerun()
