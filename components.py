# =============================================================
# frontend/components.py
# Reusable Streamlit UI components for Money Matters.
#
# Every visual element used across multiple pages lives here.
# Pages call these functions — never duplicate HTML/CSS inline.
# =============================================================

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import streamlit as st

from frontend.styles import COLORS
from utils.formatters import relative_time, truncate_text


import base64

# ── Logo — base64-encoded SVG via <img> tag (Streamlit strips raw <svg>) ──────
_SVG_SOURCE = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120">
  <ellipse cx="52" cy="108" rx="26" ry="6" fill="rgba(0,0,0,0.08)"/>
  <ellipse cx="50" cy="72" rx="28" ry="9" fill="#f0f0f0" stroke="#1a1a1a" stroke-width="2"/>
  <rect x="22" y="72" width="56" height="8" fill="#f0f0f0" stroke="#1a1a1a" stroke-width="1.5"/>
  <rect x="22" y="76" width="56" height="4" fill="#F4C430"/>
  <rect x="22" y="82" width="56" height="8" fill="#f0f0f0" stroke="#1a1a1a" stroke-width="1.5"/>
  <rect x="22" y="86" width="56" height="4" fill="#F4C430"/>
  <ellipse cx="50" cy="90" rx="28" ry="9" fill="#e8e8e8" stroke="#1a1a1a" stroke-width="2"/>
  <clipPath id="cc"><rect x="22" y="72" width="56" height="26"/></clipPath>
  <g clip-path="url(#cc)" stroke="#c8c8c8" stroke-width="1" opacity="0.5">
    <line x1="22" y1="70" x2="78" y2="100"/>
    <line x1="30" y1="70" x2="86" y2="100"/>
    <line x1="14" y1="70" x2="70" y2="100"/>
    <line x1="6"  y1="70" x2="62" y2="100"/>
    <line x1="-2" y1="70" x2="54" y2="100"/>
  </g>
  <ellipse cx="82" cy="86" rx="10" ry="10" fill="#e8e8e8" stroke="#1a1a1a" stroke-width="2"/>
  <ellipse cx="82" cy="86" rx="7"  ry="7"  fill="#f0f0f0" stroke="#1a1a1a" stroke-width="1"/>
  <line x1="50" y1="72" x2="50" y2="36" stroke="#1a1a1a" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M50 54 Q32 40 28 22 Q44 28 50 48" fill="#a8d8b0" stroke="#1a1a1a" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M50 46 Q68 30 72 12 Q56 20 50 42" fill="#2ECC9B" stroke="#1a1a1a" stroke-width="1.5" stroke-linejoin="round"/>
  <line x1="50" y1="48" x2="34" y2="30" stroke="#1a1a1a" stroke-width="1" opacity="0.4"/>
  <line x1="50" y1="42" x2="66" y2="20" stroke="#1a1a1a" stroke-width="1" opacity="0.4"/>
  <text x="10" y="30" font-size="11" fill="#F4C430" font-family="sans-serif">&#10022;</text>
  <text x="66" y="18" font-size="9"  fill="#F4C430" font-family="sans-serif">&#10022;</text>
  <text x="70" y="40" font-size="7"  fill="#F4C430" font-family="sans-serif">&#10022;</text>
</svg>"""

# Encode as base64 data URI so Streamlit renders it inside <img> (not filtered)
_LOGO_B64 = base64.b64encode(_SVG_SOURCE.encode("utf-8")).decode("utf-8")
_PNG_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo1.png"


def _logo_img_html(width: int = 84) -> str:
    """Return the preferred logo image tag, falling back to the inline SVG."""
    try:
        if _PNG_LOGO_PATH.exists():
            logo_b64 = base64.b64encode(_PNG_LOGO_PATH.read_bytes()).decode("ascii")
            return (
                f'<img src="data:image/png;base64,{logo_b64}" width="{width}" '
                f'style="flex-shrink:0;" alt="Money Matters logo">'
            )
    except OSError:
        pass
    return (
        f'<img src="data:image/svg+xml;base64,{_LOGO_B64}" width="{width}" '
        f'style="flex-shrink:0;" alt="Money Matters logo">'
    )


# ── Logo ──────────────────────────────────────────────────────

def render_logo(compact: bool = False) -> None:
    """Render the Money Matters logo with the dashboard brand styling."""
    logo_img = _logo_img_html(72 if compact else 84)
    if compact:
        st.markdown(
            f"""
            <div class="mm-logo" style="display:flex;align-items:center;gap:10px;
                                        padding:0.75rem 0.5rem 0.25rem;">
                {logo_img}
                <div style="line-height:1.2;">
                    <div class="logo-text">Money Matters</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="mm-logo" style="display:flex;align-items:center;gap:12px;
                                        padding:1rem 0.5rem 0.5rem;">
                {logo_img}
                <div style="line-height:1.3;">
                    <div class="logo-text">MONEY<br><span>MATTERS</span></div>
                    <div class="logo-tagline">Your AI Financial Companion</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Divider ───────────────────────────────────────────────────

def divider(margin: str = "0.5rem 0") -> None:
    """Render a subtle horizontal divider."""
    st.markdown(
        f'<hr style="margin:{margin};border-top:1px solid {COLORS["border"]};">',
        unsafe_allow_html=True,
    )


# ── Intent badge ──────────────────────────────────────────────

_INTENT_ICONS = {
    "calculator"       : "🧮",
    "rag"              : "📚",
    "deep_dive"        : "🔬",
    "web_search"       : "🌐",
    "government_scheme": "🏛️",
    "fraud_awareness"  : "🛡️",
    "investment"       : "📈",
    "loan"             : "🏠",
    "tax"              : "📋",
    "banking"          : "🏦",
    "upi_help"         : "📱",
    "consumer_rights"  : "⚖️",
    "daily_brief"      : "📰",
    "normal_chat"      : "💬",
}


def intent_badge(intent_value: str, label: str) -> None:
    """Render a small coloured intent badge."""
    icon = _INTENT_ICONS.get(intent_value, "💬")
    st.markdown(
        f'<span class="mm-intent-badge">{icon} {label}</span>',
        unsafe_allow_html=True,
    )


# ── Source citations ──────────────────────────────────────────

def source_tags(sources: list[str]) -> None:
    """Render a row of source citation tags."""
    if not sources:
        return
    tags = "".join(
        f'<span class="mm-source">📌 {s}</span>' for s in sources
    )
    st.markdown(
        f'<div style="margin-top:0.5rem;">{tags}</div>',
        unsafe_allow_html=True,
    )


# ── Feature cards (home page) ─────────────────────────────────

def feature_card(
    icon      : str,
    title     : str,
    desc      : str,
    cta       : str,
    on_click  : Callable,
    key       : str,
) -> None:
    """Render a clickable feature card."""
    st.markdown(
        f"""
        <div class="mm-feature-card">
            <span class="icon">{icon}</span>
            <h4>{title}</h4>
            <p>{desc}</p>
            <span class="cta">{cta} →</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Hidden button for click detection
    if st.button(cta, key=key, use_container_width=True):
        on_click()


# ── News card (Daily Brief) ───────────────────────────────────

def news_card(article) -> None:
    """
    Render a single news article card.
    `article` is a NewsArticle instance.
    """
    display_summary = article.ai_summary or article.summary
    time_str        = article.display_time

    st.markdown(
        f"""
        <div class="mm-news-card">
            <div class="news-title">{article.title}</div>
            <div class="news-meta">
                <span>📰 {article.source}</span>
                {"<span>·</span><span>" + time_str + "</span>" if time_str else ""}
            </div>
            {f'<div class="news-summary">{display_summary}</div>' if display_summary else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if article.url:
        st.markdown(
            f'<a href="{article.url}" target="_blank" style="font-size:12px;'
            f'color:{COLORS["primary"]};text-decoration:none;">Read More →</a>',
            unsafe_allow_html=True,
        )


# ── Calculator result card ────────────────────────────────────

def calc_result_card(primary_label: str, primary_value: str) -> None:
    """Render the hero result card for calculator outputs."""
    st.markdown(
        f"""
        <div class="mm-calc-result">
            <div class="result-label">{primary_label}</div>
            <div class="result-value">{primary_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def calc_breakdown_table(rows: dict[str, str]) -> None:
    """Render a clean key-value breakdown table for calc results."""
    items = "".join(
        f"""
        <div style="display:flex;justify-content:space-between;
                    padding:0.5rem 0;border-bottom:1px solid {COLORS['border']};
                    font-size:14px;">
            <span style="color:{COLORS['text_muted']}">{k}</span>
            <span style="font-weight:600;color:{COLORS['text']}">{v}</span>
        </div>
        """
        for k, v in rows.items()
        if not k.startswith("_")  # skip _raw keys
    )
    st.markdown(
        f'<div style="margin-top:1rem;">{items}</div>',
        unsafe_allow_html=True,
    )


# ── Scheme card ───────────────────────────────────────────────

def scheme_card(scheme: dict) -> None:
    """Render a government scheme info card."""
    cat   = scheme.get("category", "investment")
    badge = f'<span class="mm-scheme-badge badge-{cat}">{cat}</span>'

    benefits_html = "".join(
        f"<li style='font-size:13px;margin-bottom:4px;'>{b}</li>"
        for b in scheme.get("benefits", [])[:4]
    )

    st.markdown(
        f"""
        <div class="mm-card" style="margin-bottom:1rem;">
            <div style="display:flex;align-items:center;
                        justify-content:space-between;margin-bottom:0.5rem;">
                <h4 style="font-size:15px;font-weight:600;
                           margin:0;color:{COLORS['text']};">
                    {scheme['name']}
                </h4>
                {badge}
            </div>
            <p style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:0.75rem;">
                {scheme.get('ministry', '')}
            </p>
            <ul style="margin:0;padding-left:1.2rem;">
                {benefits_html}
            </ul>
            <div style="margin-top:0.75rem;font-size:13px;">
                <strong style="color:{COLORS['primary']};">Rate:</strong>
                {scheme.get('interest_rate', 'N/A')} &nbsp;|&nbsp;
                <strong style="color:{COLORS['primary']};">Apply:</strong>
                {scheme.get('how_to_apply', '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if scheme.get("url"):
        st.markdown(
            f'<a href="{scheme["url"]}" target="_blank" style="font-size:12px;'
            f'color:{COLORS["primary"]};">Learn More →</a>',
            unsafe_allow_html=True,
        )


# ── Sidebar conversation item ─────────────────────────────────

def sidebar_conv_item(
    title    : str,
    preview  : str,
    is_active: bool,
    key      : str,
) -> bool:
    """
    Render a clickable sidebar conversation item.
    Returns True if clicked.
    """
    active_style = (
        f"background:rgba(13,110,110,0.10);border-left:3px solid {COLORS['primary']};"
        if is_active else ""
    )
    st.markdown(
        f"""
        <div class="mm-conv-item" style="{active_style}">
            <div class="conv-title">{truncate_text(title, 38)}</div>
            <div class="conv-meta">{truncate_text(preview, 45)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.button("Open", key=key, use_container_width=True)


# ── Quick action chips ────────────────────────────────────────

def quick_action_chips(
    actions  : list[dict],   # [{"label": str, "icon": str, "key": str}]
) -> Optional[str]:
    """
    Render a row of quick-action chips.
    Returns the key of the clicked chip, or None.
    """
    cols   = st.columns(len(actions))
    clicked = None
    for col, action in zip(cols, actions):
        with col:
            if st.button(
                f"{action['icon']} {action['label']}",
                key     = action["key"],
                use_container_width=True,
            ):
                clicked = action["key"]
    return clicked


# ── Welcome header ────────────────────────────────────────────

def welcome_header(name: str) -> None:
    """Render the personalised welcome heading on the home page."""
    st.markdown(
        f"""
        <div class="mm-welcome" style="text-align:center;padding:2rem 0 1rem;">
            <h1>Welcome, <span>{name}</span>! 👋</h1>
            <p>Your AI copilot for smarter financial decisions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Section header ────────────────────────────────────────────

def section_header(title: str, subtitle: str = "") -> None:
    """Render a styled section title."""
    st.markdown(
        f"""
        <div style="margin:1.5rem 0 1rem;">
            <h3 style="font-size:17px;font-weight:700;
                       color:{COLORS['text']};margin-bottom:2px;">
                {title}
            </h3>
            {f'<p style="font-size:13px;color:{COLORS["text_muted"]};margin:0;">'
             f'{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Empty state ───────────────────────────────────────────────

def empty_state(
    icon   : str,
    title  : str,
    message: str,
) -> None:
    """Render a centred empty-state placeholder."""
    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 1rem;color:{COLORS['text_muted']};">
            <div style="font-size:3rem;margin-bottom:0.75rem;">{icon}</div>
            <h4 style="font-size:16px;font-weight:600;
                       color:{COLORS['text']};margin-bottom:0.4rem;">
                {title}
            </h4>
            <p style="font-size:14px;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Toast notification ────────────────────────────────────────

def show_toast(message: str, icon: str = "✅") -> None:
    """Display a Streamlit toast notification."""
    st.toast(f"{icon} {message}")


# ── Status indicator ──────────────────────────────────────────

def status_dot(status: str, label: str) -> None:
    """Render a coloured status dot with label (ok/warning/error)."""
    color_map = {
        "ok"     : COLORS["success"],
        "warning": COLORS["warning"],
        "error"  : COLORS["error"],
    }
    color = color_map.get(status, COLORS["text_muted"])
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:6px;font-size:13px;">
            <span style="width:8px;height:8px;border-radius:50%;
                         background:{color};display:inline-block;"></span>
            <span style="color:{COLORS['text']}">{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Streaming text helper ─────────────────────────────────────

def stream_response(generator, placeholder=None):
    """
    Stream text from a generator into a Streamlit write_stream call.
    If placeholder is given, updates it incrementally.

    Returns the full accumulated text.
    """
    full_text = ""
    if placeholder:
        for chunk in generator:
            full_text += chunk
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
    else:
        full_text = st.write_stream(generator)
    return full_text


__all__ = [
    "render_logo",
    "divider",
    "intent_badge",
    "source_tags",
    "feature_card",
    "news_card",
    "calc_result_card",
    "calc_breakdown_table",
    "scheme_card",
    "sidebar_conv_item",
    "quick_action_chips",
    "welcome_header",
    "section_header",
    "empty_state",
    "show_toast",
    "status_dot",
    "stream_response",
]
