from __future__ import annotations

import streamlit as st

from backend.auth_backend import AuthError, login_with_email, register_user
from backend.history import load_all_conversations, save_conversation
from backend.session import login_user, set_ui_mode, set_toast
from frontend.components import divider, render_logo
from frontend.styles import COLORS


def _claim_guest_history(user_id: str) -> dict:
    """Persist guest conversations once a user signs in."""
    merged = load_all_conversations(user_id)
    session_conversations = st.session_state.get("conversations", {})

    for conv_id, conv in session_conversations.items():
        if conv.message_count == 0:
            continue
        conv.user_id = user_id
        merged[conv_id] = conv
        save_conversation(user_id, conv)

    return merged


def render_auth_page() -> None:
    """Render the login / registration page."""
    _, col, _ = st.columns([1, 2, 1])

    with col:
        render_logo()
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="background:{COLORS['white']};
                        border:1px solid {COLORS['border']};
                        border-radius:16px;
                        padding:2rem 2.5rem;
                        box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            _render_login_form()

        with tab_register:
            _render_register_form()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        if st.button(
            "Continue as Guest ->",
            key="btn_guest",
            use_container_width=True,
        ):
            set_ui_mode("home")
            st.rerun()

        st.markdown(
            f"""
            <p style="text-align:center;font-size:12px;
                      color:{COLORS['text_muted']};margin-top:0.5rem;">
                Guest mode: conversations are not saved after the session ends.
            </p>
            """,
            unsafe_allow_html=True,
        )


def _render_login_form() -> None:
    st.markdown(
        f"""
        <h3 style="font-size:20px;font-weight:700;
                   color:{COLORS['text']};margin-bottom:0.25rem;">
            Welcome back
        </h3>
        <p style="font-size:13px;color:{COLORS['text_muted']};
                  margin-bottom:1.5rem;">
            Sign in to your account
        </p>
        """,
        unsafe_allow_html=True,
    )

    email = st.text_input(
        "Email address",
        key="login_email",
        placeholder="you@example.com",
    )
    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
        placeholder="********",
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button(
        "Sign In",
        key="btn_signin",
        use_container_width=True,
        type="primary",
    ):
        if not email or not password:
            st.error("Please enter your email and password.")
        else:
            _do_login(email, password)

    divider(margin="1.25rem 0")

    st.markdown(
        f"""
        <div style="text-align:center;font-size:13px;
                    color:{COLORS['text_muted']};margin-bottom:0.75rem;">
            Or continue with
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Sign in with Google",
        key="btn_google_login",
        use_container_width=True,
    ):
        st.info(
            "Google Sign-In: set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env to enable."
        )


def _render_register_form() -> None:
    st.markdown(
        f"""
        <h3 style="font-size:20px;font-weight:700;
                   color:{COLORS['text']};margin-bottom:0.25rem;">
            Create an account
        </h3>
        <p style="font-size:13px;color:{COLORS['text_muted']};
                  margin-bottom:1.5rem;">
            Start your financial literacy journey
        </p>
        """,
        unsafe_allow_html=True,
    )

    display_name = st.text_input(
        "Full name",
        key="reg_name",
        placeholder="Priya Sharma",
    )
    username = st.text_input(
        "Username",
        key="reg_username",
        placeholder="priya_sharma",
    )
    email = st.text_input(
        "Email",
        key="reg_email",
        placeholder="you@example.com",
    )
    password = st.text_input(
        "Password",
        key="reg_password",
        type="password",
        placeholder="Min. 8 characters",
    )
    confirm = st.text_input(
        "Confirm password",
        key="reg_confirm",
        type="password",
        placeholder="Repeat password",
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button(
        "Create Account",
        key="btn_register",
        use_container_width=True,
        type="primary",
    ):
        if not all([display_name, username, email, password, confirm]):
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            _do_register(username, email, password, display_name)


def _do_login(email: str, password: str) -> None:
    """Attempt email login and update session state."""
    try:
        user = login_with_email(email.strip(), password)
        login_user(user)
        st.session_state["conversations"] = _claim_guest_history(user.id)
        set_toast(f"Welcome back, {user.first_name}!")
        set_ui_mode("home")
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Sign-in failed. Please try again.")


def _do_register(
    username: str,
    email: str,
    password: str,
    display_name: str,
) -> None:
    """Attempt user registration and auto-login."""
    try:
        user = register_user(
            username=username.strip(),
            email=email.strip(),
            password=password,
            display_name=display_name.strip(),
        )
        login_user(user)
        st.session_state["conversations"] = _claim_guest_history(user.id)
        set_toast(f"Account created! Welcome, {user.first_name}!")
        set_ui_mode("home")
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Registration failed. Please try again.")


__all__ = ["render_auth_page"]
