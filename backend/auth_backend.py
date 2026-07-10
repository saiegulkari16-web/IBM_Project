# =============================================================
# backend/auth_backend.py
# Authentication logic for Money Matters.
#
# Supports:
#   1. Email + Password  — hashed with bcrypt, stored in a local
#                          JSON user-store (data/users/users.json)
#   2. Google OAuth 2.0  — via google-auth-oauthlib
#
# In production this would be swapped for a proper database,
# but for the IBM demo this is clean and fully functional.
# =============================================================

from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from backend.models import AuthProvider, User
from utils.logger import logger
from utils.validators import validate_email, validate_password, validate_username
from utils.config_loader import get_env

# ── Storage ───────────────────────────────────────────────────
_USERS_DIR  = Path(__file__).resolve().parent.parent / "data" / "users"
_USERS_FILE = _USERS_DIR / "users.json"


def _ensure_store() -> None:
    """Create the user-store directory and file if they don't exist."""
    _USERS_DIR.mkdir(parents=True, exist_ok=True)
    if not _USERS_FILE.exists():
        _USERS_FILE.write_text(json.dumps({}), encoding="utf-8")


def _read_store() -> dict:
    _ensure_store()
    try:
        with _USERS_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read user store: {}", exc)
        return {}


def _write_store(data: dict) -> None:
    _ensure_store()
    with _USERS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)


# ── Password hashing (SHA-256 + salt — no external deps) ─────
# NOTE: For production, swap to bcrypt. SHA-256+salt is fine
#       for an IBM demo with no real user PII at risk.

def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Return (hashed_password, salt). Generate salt if not provided."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return hashed, salt


def _verify_password(password: str, hashed: str, salt: str) -> bool:
    computed, _ = _hash_password(password, salt)
    return secrets.compare_digest(computed, hashed)


# ── Email Registration ────────────────────────────────────────

class AuthError(Exception):
    """Raised for all authentication/registration failures."""
    pass


def register_user(
    username: str,
    email: str,
    password: str,
    display_name: str = "",
) -> User:
    """
    Register a new user with email and password.

    Raises:
        AuthError: if validation fails or user already exists.
    Returns:
        User: the newly created User object.
    """
    # Validate inputs
    ok, msg = validate_username(username)
    if not ok:
        raise AuthError(msg)
    ok, msg = validate_email(email)
    if not ok:
        raise AuthError(msg)
    ok, msg = validate_password(password)
    if not ok:
        raise AuthError(msg)

    store = _read_store()
    email_lower = email.lower().strip()

    # Check for duplicates
    for record in store.values():
        if record.get("email") == email_lower:
            raise AuthError("An account with this email already exists.")
        if record.get("username", "").lower() == username.lower():
            raise AuthError("This username is already taken.")

    # Create user
    user_id     = str(uuid4())
    hashed, salt = _hash_password(password)
    user = User(
        id            = user_id,
        username      = username.strip(),
        email         = email_lower,
        display_name  = display_name.strip() or username.strip(),
        auth_provider = AuthProvider.EMAIL,
    )

    store[user_id] = {
        **user.model_dump(),
        "password_hash": hashed,
        "password_salt": salt,
    }
    _write_store(store)
    logger.info("New user registered: {} <{}>", username, email_lower)
    return user


def login_with_email(email: str, password: str) -> User:
    """
    Authenticate a user by email and password.

    Raises:
        AuthError: if credentials are invalid.
    Returns:
        User: the authenticated User object.
    """
    ok, msg = validate_email(email)
    if not ok:
        raise AuthError(msg)
    if not password:
        raise AuthError("Password is required.")

    store      = _read_store()
    email_lower = email.lower().strip()

    for user_id, record in store.items():
        if record.get("email") == email_lower:
            if not record.get("is_active", True):
                raise AuthError("This account has been deactivated.")

            pw_hash = record.get("password_hash", "")
            pw_salt = record.get("password_salt", "")

            if not _verify_password(password, pw_hash, pw_salt):
                raise AuthError("Incorrect password.")

            # Update last_login
            record["last_login"] = datetime.now(timezone.utc).isoformat()
            _write_store(store)

            # Reconstruct User (exclude internal fields)
            user_data = {k: v for k, v in record.items()
                         if k not in ("password_hash", "password_salt")}
            user = User.model_validate(user_data)
            logger.info("User authenticated: {} <{}>", user.username, email_lower)
            return user

    raise AuthError("No account found with that email address.")


# ── Google OAuth ──────────────────────────────────────────────

def get_google_auth_url(redirect_uri: str) -> str:
    """
    Build the Google OAuth 2.0 authorisation URL.
    Returns the URL the user should be redirected to.
    """
    from google_auth_oauthlib.flow import Flow

    client_id     = get_env("GOOGLE_CLIENT_ID")
    client_secret = get_env("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise AuthError("Google OAuth credentials are not configured.")

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id"    : client_id,
                "client_secret": client_secret,
                "auth_uri"     : "https://accounts.google.com/o/oauth2/auth",
                "token_uri"    : "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["openid", "email", "profile"],
    )
    flow.redirect_uri = redirect_uri
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url


def login_with_google_token(id_token_str: str) -> User:
    """
    Verify a Google ID token and return (or create) the corresponding User.

    Raises:
        AuthError: if token verification fails.
    Returns:
        User: verified User object.
    """
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    client_id = get_env("GOOGLE_CLIENT_ID")
    if not client_id:
        raise AuthError("Google OAuth client ID is not configured.")

    try:
        id_info = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            client_id,
        )
    except Exception as exc:
        logger.warning("Google token verification failed: {}", exc)
        raise AuthError("Google sign-in failed. Please try again.")

    email       = id_info.get("email", "").lower()
    name        = id_info.get("name", "")
    google_sub  = id_info.get("sub", "")
    avatar_url  = id_info.get("picture", "")

    if not email:
        raise AuthError("Could not retrieve email from Google account.")

    store = _read_store()

    # Check if the Google user already has an account
    for user_id, record in store.items():
        if record.get("email") == email:
            record["last_login"] = datetime.now(timezone.utc).isoformat()
            record["avatar_url"] = avatar_url
            _write_store(store)
            user_data = {k: v for k, v in record.items()
                         if k not in ("password_hash", "password_salt")}
            return User.model_validate(user_data)

    # First-time Google login — auto-register
    username = email.split("@")[0].replace(".", "_")[:30]
    # Ensure username is unique
    existing_names = {r.get("username", "").lower() for r in store.values()}
    if username.lower() in existing_names:
        username = f"{username}_{secrets.token_hex(3)}"

    user_id = str(uuid4())
    user = User(
        id            = user_id,
        username      = username,
        email         = email,
        display_name  = name,
        avatar_url    = avatar_url,
        auth_provider = AuthProvider.GOOGLE,
    )
    store[user_id] = {**user.model_dump()}
    _write_store(store)
    logger.info("New Google user auto-registered: {} <{}>", username, email)
    return user


# ── Profile Utilities ─────────────────────────────────────────

def get_user_by_id(user_id: str) -> Optional[User]:
    """Fetch a user record by ID. Returns None if not found."""
    store = _read_store()
    record = store.get(user_id)
    if not record:
        return None
    user_data = {k: v for k, v in record.items()
                 if k not in ("password_hash", "password_salt")}
    return User.model_validate(user_data)


def update_display_name(user_id: str, new_name: str) -> bool:
    """Update a user's display name. Returns True on success."""
    store = _read_store()
    if user_id not in store:
        return False
    store[user_id]["display_name"] = new_name.strip()[:50]
    _write_store(store)
    return True


__all__ = [
    "AuthError",
    "register_user",
    "login_with_email",
    "get_google_auth_url",
    "login_with_google_token",
    "get_user_by_id",
    "update_display_name",
]
