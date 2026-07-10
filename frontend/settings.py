# =============================================================
# frontend/settings.py
# Settings page for Money Matters.
#
# Sections:
#   • Profile (display name update)
#   • IBM Services health check (watsonx + COS)
#   • RAG index status
#   • App info / version
# =============================================================

from __future__ import annotations

import streamlit as st

from backend.session import (
    get_current_user,
    is_authenticated,
    login_user,
    set_ui_mode,
)
from frontend.components import (
    section_header,
    divider,
    status_dot,
    empty_state,
)
from frontend.styles import COLORS


def render_settings() -> None:
    """Render the Settings page."""

    section_header("⚙️ Settings", "Configure your Money Matters experience")
    divider()

    user = get_current_user()
    auth = is_authenticated()

    tab_profile, tab_services, tab_rag, tab_about = st.tabs([
        "Profile", "IBM Services", "RAG Index", "About",
    ])

    # ── Profile ───────────────────────────────────────────
    with tab_profile:
        st.markdown(
            f"<h4 style='margin-bottom:1rem;font-size:16px;'>👤 Profile</h4>",
            unsafe_allow_html=True,
        )
        if not auth or not user:
            empty_state(
                "🔒",
                "Not signed in",
                "Sign in to manage your profile.",
            )
            if st.button("Sign In", key="settings_signin", type="primary"):
                set_ui_mode("login")
                st.rerun()
        else:
            st.markdown(
                f"""
                <div style="background:{COLORS['surface']};
                            border:1px solid {COLORS['border']};
                            border-radius:12px;padding:1.2rem 1.5rem;
                            margin-bottom:1.25rem;">
                    <div style="font-size:13px;color:{COLORS['text_muted']};">
                        Signed in as
                    </div>
                    <div style="font-size:15px;font-weight:600;
                                color:{COLORS['text']};margin-top:2px;">
                        {user.display_name or user.username}
                    </div>
                    <div style="font-size:13px;color:{COLORS['text_muted']};">
                        {user.email}
                    </div>
                    <div style="font-size:11px;color:{COLORS['text_muted']};
                                margin-top:4px;">
                        Auth: {user.auth_provider} · 
                        Member since {user.created_at.strftime('%b %Y') if user.created_at else 'N/A'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Update display name
            new_name = st.text_input(
                "Display Name",
                value = user.display_name or user.username,
                key   = "settings_display_name",
            )
            if st.button("Update Name", key="btn_update_name", type="primary"):
                from backend.auth_backend import update_display_name
                if update_display_name(user.id, new_name):
                    user.display_name = new_name.strip()
                    login_user(user)   # refresh session
                    st.success("Display name updated!")
                else:
                    st.error("Update failed.")

    # ── IBM Services ──────────────────────────────────────
    with tab_services:
        st.markdown(
            "<h4 style='margin-bottom:1rem;font-size:16px;'>☁️ IBM Service Status</h4>",
            unsafe_allow_html=True,
        )

        # watsonx.ai
        with st.spinner("Checking IBM watsonx.ai..."):
            try:
                from services.watsonx_service import health_check as wx_check
                wx_status = wx_check()
            except Exception as e:
                wx_status = {"status": "error", "message": str(e),
                             "model_id": "N/A", "url": "N/A"}

        _render_service_card(
            title    = "IBM watsonx.ai",
            icon     = "🤖",
            status   = wx_status["status"],
            details  = {
                "Model"  : wx_status.get("model_id", "N/A"),
                "Region" : "us-south (Dallas)",
                "URL"    : wx_status.get("url", "N/A"),
                "Message": wx_status.get("message", ""),
            },
        )

        divider(margin="1rem 0")

        # IBM COS
        with st.spinner("Checking IBM Cloud Object Storage..."):
            try:
                from services.cos_service import health_check as cos_check
                cos_status = cos_check()
            except Exception as e:
                cos_status = {"status": "error", "message": str(e),
                              "bucket": "N/A", "region": "N/A"}

        _render_service_card(
            title  = "IBM Cloud Object Storage",
            icon   = "🗄️",
            status = cos_status["status"],
            details= {
                "Bucket" : cos_status.get("bucket", "N/A"),
                "Region" : cos_status.get("region", "us-south (Dallas)"),
                "Message": cos_status.get("message", ""),
            },
        )

    # ── RAG Index ────────────────────────────────────────
    with tab_rag:
        st.markdown(
            "<h4 style='margin-bottom:1rem;font-size:16px;'>🔍 RAG Knowledge Base</h4>",
            unsafe_allow_html=True,
        )

        try:
            from rag.pipeline import get_index_status
            idx = get_index_status()
        except Exception as e:
            idx = {"ready": False, "message": str(e)}

        if idx.get("ready"):
            status_dot("ok", "Index Ready")
            st.markdown(
                f"""
                <div style="margin-top:0.75rem;font-size:13px;
                            color:{COLORS['text_muted']};">
                    <strong>Vectors:</strong> {idx.get('vectors', 'N/A')} &nbsp;|&nbsp;
                    <strong>Chunks:</strong> {idx.get('chunks', 'N/A')}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            status_dot("error", "Index not built")
            st.markdown(
                f"""
                <div style="margin-top:0.5rem;font-size:13px;
                            color:{COLORS['text_muted']};">
                    {idx.get('message', '')}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.info(
                "Run `python scripts/build_vectorstore.py` to build the RAG index.",
                icon="ℹ️",
            )

        divider(margin="1rem 0")

        if st.button("🔄 Rebuild Index", key="btn_rebuild_idx"):
            with st.spinner("Rebuilding RAG index... this may take a few minutes."):
                try:
                    from rag.pipeline import ingest_and_index
                    result = ingest_and_index()
                    if result.get("status") == "success":
                        st.success(
                            f"Index rebuilt: {result['chunks']} chunks, "
                            f"{result['vectors']} vectors."
                        )
                    else:
                        st.error(result.get("message", "Rebuild failed."))
                except Exception as e:
                    st.error(str(e))

    # ── About ────────────────────────────────────────────
    with tab_about:
        st.markdown(
            f"""
            <div style="padding:1rem 0;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">💰</div>
                <h3 style="font-size:20px;font-weight:700;color:{COLORS['primary']};
                           margin-bottom:0.25rem;">Money Matters</h3>
                <p style="font-size:14px;color:{COLORS['text_muted']};
                          margin-bottom:1.5rem;">
                    Smarter Money. Better Decisions.
                </p>
                <div style="font-size:13px;color:{COLORS['text']};
                            line-height:2;">
                    <strong>Version:</strong> 1.0.0<br>
                    <strong>Built for:</strong> IBM SkillsBuild Internship 2025<br>
                    <strong>AI Model:</strong> IBM Granite (ibm/granite-13b-chat-v2)<br>
                    <strong>Region:</strong> Dallas (us-south)<br>
                    <strong>Framework:</strong> Streamlit + Python 3.11+<br>
                    <strong>RAG:</strong> FAISS + sentence-transformers<br>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_service_card(
    title  : str,
    icon   : str,
    status : str,
    details: dict,
) -> None:
    """Render a service status card."""
    status_color = {
        "ok"   : COLORS["success"],
        "error": COLORS["error"],
    }.get(status, COLORS["warning"])

    status_text = "Connected" if status == "ok" else "Disconnected"

    details_html = "".join(
        f"""
        <div style="display:flex;gap:0.5rem;font-size:12px;margin-top:3px;">
            <span style="color:{COLORS['text_muted']};min-width:60px;">{k}:</span>
            <span style="color:{COLORS['text']}">{v}</span>
        </div>
        """
        for k, v in details.items() if v
    )

    st.markdown(
        f"""
        <div style="background:{COLORS['white']};
                    border:1px solid {COLORS['border']};
                    border-radius:12px;padding:1.1rem 1.5rem;">
            <div style="display:flex;align-items:center;
                        justify-content:space-between;margin-bottom:0.75rem;">
                <span style="font-size:15px;font-weight:600;color:{COLORS['text']};">
                    {icon} {title}
                </span>
                <span style="font-size:12px;font-weight:600;padding:3px 10px;
                             border-radius:20px;
                             background:{status_color}22;color:{status_color};">
                    ● {status_text}
                </span>
            </div>
            {details_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


__all__ = ["render_settings"]
