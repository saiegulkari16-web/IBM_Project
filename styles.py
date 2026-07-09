from __future__ import annotations

import streamlit as st


COLORS = {
    "primary": "#0E7373",
    "primary_light": "#21B5A9",
    "primary_dark": "#0A5B5B",
    "secondary": "#EAF8F5",
    "accent": "#F4C95D",
    "bg": "#FBF8F3",
    "surface": "#F6F2EA",
    "border": "#ECE4D8",
    "text": "#17304D",
    "text_muted": "#6A7483",
    "white": "#FFFFFF",
    "sidebar_bg": "#FCF9F4",
    "success": "#1FA55B",
    "warning": "#D97706",
    "error": "#DC2626",
}


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
    --primary: {primary};
    --primary-light: {primary_light};
    --primary-dark: {primary_dark};
    --secondary: {secondary};
    --accent: {accent};
    --bg: {bg};
    --surface: {surface};
    --border: {border};
    --text: {text};
    --text-muted: {text_muted};
    --white: {white};
    --shadow-soft: 0 10px 32px rgba(17, 39, 70, 0.06);
    --shadow-card: 0 12px 36px rgba(17, 39, 70, 0.08);
}}

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif !important;
    background:
        radial-gradient(circle at top right, rgba(33,181,169,0.12), transparent 24%),
        radial-gradient(circle at bottom center, rgba(244,201,93,0.10), transparent 22%),
        var(--bg) !important;
    color: var(--text) !important;
}}

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
    display: none !important;
}}

[data-testid="stSidebar"] {{
    background: var(--sidebar-bg, {sidebar_bg}) !important;
    border-right: 1px solid rgba(236,228,216,0.75) !important;
}}

[data-testid="stSidebar"] > div {{
    padding-top: 0.75rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}

[data-testid="stMainBlockContainer"],
.block-container {{
    max-width: 100% !important;
}}

.block-container {{
    padding: 1.4rem 1.8rem 2rem !important;
}}

.stButton > button {{
    border-radius: 999px !important;
    border: 1px solid rgba(236,228,216,0.95) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
    box-shadow: none !important;
}}

.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-soft) !important;
}}

.stButton > button[kind="primary"],
.stButton button[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
    color: white !important;
    border-color: transparent !important;
}}

.stButton > button[kind="secondary"] {{
    background: rgba(255,255,255,0.72) !important;
    color: var(--text) !important;
}}

.stTextInput input,
.stTextArea textarea,
[data-testid="stChatInput"] textarea,
.stSelectbox > div > div,
.stNumberInput input {{
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    color: var(--text) !important;
}}

.stTextInput input {{
    height: 64px !important;
    font-size: 17px !important;
    padding-left: 1.2rem !important;
}}

.stTextInput input:focus,
.stTextArea textarea:focus,
[data-testid="stChatInput"] textarea:focus {{
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(14,115,115,0.10) !important;
}}

.mm-logo {{
    align-items: center;
}}

.mm-logo img {{
    width: 74px;
    height: auto;
}}

.mm-logo .logo-text {{
    font-size: 23px;
    font-weight: 800;
    line-height: 0.94;
    letter-spacing: -0.03em;
    color: var(--text);
}}

.mm-logo .logo-text span {{
    color: var(--primary-light);
}}

.mm-logo .logo-tagline {{
    font-size: 11px;
    color: var(--text);
    margin-top: 10px;
}}

.mm-sidebar-spacer {{
    height: 0.75rem;
}}

.mm-home-sidebar {{
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(236,228,216,0.92);
    border-radius: 28px;
    padding: 0.5rem 0.7rem 1rem;
    box-shadow: var(--shadow-soft);
    min-height: 86vh;
}}

.mm-home-side-gap {{
    height: 0.8rem;
}}

.mm-home-recent-title {{
    font-size: 14px;
    font-weight: 800;
    color: var(--primary);
    margin: 0.9rem 0 0.35rem;
    padding-left: 0.3rem;
}}

.mm-home-recent-time {{
    height: 40px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    color: var(--text-muted);
    font-size: 11px;
    white-space: nowrap;
}}

.mm-sidebar-gap {{
    height: 0.5rem;
}}

.mm-sidebar-footer-gap {{
    height: 1rem;
}}

.mm-sidebar-section-title {{
    font-size: 14px;
    font-weight: 800;
    color: var(--primary);
    margin: 0.8rem 0 0.3rem;
    padding-left: 0.15rem;
}}

.mm-nav-badge-row {{
    display: flex;
    justify-content: flex-end;
    margin-top: -2.45rem;
    margin-bottom: 1.4rem;
    padding-right: 0.65rem;
    pointer-events: none;
}}

.mm-nav-badge-row span {{
    background: #FFD56F;
    color: #805300;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    padding: 0.18rem 0.52rem;
}}

.mm-recent-time {{
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    font-size: 12px;
    color: var(--text-muted);
    white-space: nowrap;
}}

.mm-user-card {{
    background: rgba(255,255,255,0.78);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.95rem 1rem;
    box-shadow: var(--shadow-soft);
}}

.mm-user-name {{
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
}}

.mm-user-email {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 0.2rem;
}}

.mm-top-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 999px;
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--border);
    color: var(--text);
    font-size: 18px;
    box-shadow: var(--shadow-soft);
}}

.mm-welcome {{
    text-align: center;
    padding: 0.9rem 0 1.2rem;
}}

.mm-welcome h1 {{
    font-size: 3.2rem;
    font-weight: 800;
    color: #13386A;
    margin: 0;
    letter-spacing: -0.03em;
}}

.mm-welcome h1 span {{
    color: var(--primary-light);
}}

.mm-welcome p {{
    font-size: 17px;
    color: var(--text);
    margin-top: 0.45rem;
}}

.mm-soft-card,
.mm-brief-panel,
.mm-hero-banner {{
    background: rgba(255,255,255,0.9);
    border: 1px solid rgba(236,228,216,0.95);
    border-radius: 26px;
    box-shadow: var(--shadow-soft);
}}

.mm-home-composer-shell {{
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(236,228,216,0.95);
    border-radius: 28px;
    box-shadow: var(--shadow-soft);
    padding: 1.25rem 1.3rem;
}}

.mm-badge-card {{
    padding: 1rem 1.15rem;
}}

.mm-badge-title {{
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
}}

.mm-badge-subtitle {{
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 0.18rem;
}}

.mm-feature-card {{
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,251,250,0.96));
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.35rem;
    min-height: 188px;
    box-shadow: 0 2px 6px rgba(17,39,70,0.03);
}}

.mm-feature-card .icon {{
    display: inline-block;
    font-size: 15px;
    font-weight: 700;
    color: var(--primary-light);
    margin-bottom: 0.85rem;
}}

.mm-feature-card h4 {{
    font-size: 15px;
    font-weight: 700;
    margin: 0 0 0.45rem;
    color: var(--text);
}}

.mm-feature-card p {{
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.55;
    margin: 0;
}}

.mm-brief-panel {{
    padding: 1.15rem;
}}

.mm-brief-hero {{
    min-height: 156px;
    border-radius: 22px;
    padding: 1rem;
    background:
        radial-gradient(circle at top right, rgba(214,245,238,0.95), transparent 36%),
        linear-gradient(135deg, #fffef9, #eff9f7);
    display: flex;
    align-items: flex-start;
}}

.mm-brief-kicker {{
    font-size: 16px;
    font-weight: 800;
    color: var(--text);
}}

.mm-brief-date {{
    margin-top: 0.4rem;
    font-size: 13px;
    color: var(--text-muted);
}}

.mm-brief-heading {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    font-weight: 700;
    margin: 1rem 0 0.9rem;
    color: var(--text);
}}

.mm-news-card {{
    background: linear-gradient(180deg, rgba(238,247,252,0.92), rgba(255,255,255,0.96));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1rem 0.95rem;
    margin-bottom: 0.85rem;
}}

.mm-news-card .news-title {{
    font-size: 13px;
    font-weight: 800;
    color: var(--text);
    line-height: 1.48;
}}

.mm-news-card .news-meta,
.mm-news-card .news-summary {{
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 0.46rem;
}}

.mm-hero-banner {{
    padding: 1.25rem 1.6rem;
    background:
        radial-gradient(circle at right bottom, rgba(244,201,93,0.24), transparent 28%),
        linear-gradient(135deg, #FFF6D9, #FFFDF5 56%, #EEF8F5);
}}

.mm-hero-title {{
    font-size: 17px;
    font-weight: 800;
    color: var(--text);
}}

.mm-hero-subtitle {{
    font-size: 14px;
    color: var(--text);
    margin-top: 0.32rem;
}}

.mm-intent-badge,
.mm-source {{
    border-radius: 999px;
}}

[data-testid="stSidebar"] .stButton {{
    margin-bottom: 0.42rem !important;
}}

.mm-home-sidebar .stButton {{
    margin-bottom: 0.45rem !important;
}}

.mm-home-sidebar .stButton > button {{
    min-height: 46px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 1rem !important;
    font-weight: 500 !important;
    background: transparent !important;
    border-color: transparent !important;
    color: var(--text) !important;
}}

.mm-home-sidebar .stButton > button:hover {{
    background: rgba(14,115,115,0.06) !important;
}}

.mm-home-sidebar button[kind="primary"] {{
    background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: var(--shadow-soft) !important;
}}

[data-testid="stSidebar"] .stButton > button {{
    min-height: 46px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 1rem !important;
    font-weight: 500 !important;
    background: transparent !important;
    border-color: transparent !important;
    color: var(--text) !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(14,115,115,0.06) !important;
}}

[data-testid="stSidebar"] button[kind="primary"] {{
    background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: var(--shadow-soft) !important;
}}

[data-testid="stSidebar"] div[data-testid="column"] .stButton > button {{
    min-height: 38px !important;
    padding-left: 0.8rem !important;
    font-size: 13px !important;
}}

[data-testid="chatAvatarIcon-user"] {{
    background: var(--primary) !important;
}}

[data-testid="chatAvatarIcon-assistant"] {{
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
}}

@media (max-width: 768px) {{
    .block-container {{
        padding: 1rem !important;
    }}

    .mm-welcome h1 {{
        font-size: 2.2rem;
    }}
}}
"""


def apply_theme() -> None:
    st.markdown(f"<style>{_CSS.format(**COLORS)}</style>", unsafe_allow_html=True)


def inject_css(css: str) -> None:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


__all__ = ["COLORS", "apply_theme", "inject_css"]
