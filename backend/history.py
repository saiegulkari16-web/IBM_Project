# =============================================================
# backend/history.py
# Conversation history persistence for Money Matters.
#
# Storage strategy:
#   • Anonymous users  → in-memory only (session_state)
#   • Logged-in users  → persisted to local JSON files under
#                        data/conversations/<user_id>/
#   • When IBM COS is configured, files are mirrored to the
#     bucket for cross-session access (handled by cos_service).
#
# The JSON format is one file per conversation, named by conv_id.
# =============================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.models import Conversation, ChatMessage, ConversationStatus
from utils.logger import logger
from utils.formatters import sanitise_filename

# ── Storage root ─────────────────────────────────────────────
_DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "conversations"


def _user_dir(user_id: str) -> Path:
    """Return (and create if needed) the storage directory for a user."""
    d = _DATA_ROOT / sanitise_filename(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _conv_path(user_id: str, conv_id: str) -> Path:
    return _user_dir(user_id) / f"{conv_id}.json"


# ── Save ──────────────────────────────────────────────────────

def save_conversation(user_id: str, conversation: Conversation) -> bool:
    """
    Persist a Conversation to disk as JSON.
    Returns True on success, False on failure.
    """
    if not user_id or user_id == "anonymous":
        logger.debug("Skipping persist — anonymous user.")
        return False

    try:
        path = _conv_path(user_id, conversation.id)
        conversation.updated_at = datetime.now(timezone.utc)
        with path.open("w", encoding="utf-8") as fh:
            fh.write(conversation.model_dump_json(indent=2))
        logger.debug("Conversation {} saved to {}", conversation.id, path)
        return True
    except Exception as exc:
        logger.error("Failed to save conversation {}: {}", conversation.id, exc)
        return False


# ── Load single ───────────────────────────────────────────────

def load_conversation(user_id: str, conv_id: str) -> Optional[Conversation]:
    """
    Load a single Conversation from disk.
    Returns None if not found or on parse error.
    """
    path = _conv_path(user_id, conv_id)
    if not path.exists():
        logger.warning("Conversation file not found: {}", path)
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        conv = Conversation.model_validate(data)
        logger.debug("Conversation {} loaded.", conv_id)
        return conv
    except Exception as exc:
        logger.error("Failed to load conversation {}: {}", conv_id, exc)
        return None


# ── Load all for a user ───────────────────────────────────────

def load_all_conversations(user_id: str) -> dict[str, Conversation]:
    """
    Load all conversations for a given user from disk.
    Returns a dict keyed by conversation ID.
    Skips any files that fail to parse.
    """
    if not user_id or user_id == "anonymous":
        return {}

    user_dir = _user_dir(user_id)
    conversations: dict[str, Conversation] = {}

    for path in sorted(user_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        conv_id = path.stem
        conv = load_conversation(user_id, conv_id)
        if conv and conv.status != ConversationStatus.DELETED:
            conversations[conv.id] = conv

    logger.info("Loaded {} conversations for user {}.", len(conversations), user_id)
    return conversations


# ── Delete ────────────────────────────────────────────────────

def delete_conversation(user_id: str, conv_id: str, soft: bool = True) -> bool:
    """
    Delete a conversation.
    soft=True  → marks status as DELETED and re-saves (recoverable)
    soft=False → removes the JSON file from disk permanently
    """
    if soft:
        conv = load_conversation(user_id, conv_id)
        if conv:
            conv.status = ConversationStatus.DELETED
            return save_conversation(user_id, conv)
        return False

    path = _conv_path(user_id, conv_id)
    if path.exists():
        path.unlink()
        logger.info("Conversation {} permanently deleted.", conv_id)
        return True
    return False


# ── Update title ──────────────────────────────────────────────

def update_conversation_title(
    user_id: str,
    conv_id: str,
    title: str,
) -> bool:
    """Persist a new title for an existing conversation."""
    conv = load_conversation(user_id, conv_id)
    if not conv:
        return False
    conv.title = title.strip()[:80]   # cap at 80 chars
    return save_conversation(user_id, conv)


# ── Pin / Unpin ───────────────────────────────────────────────

def toggle_pin(user_id: str, conv_id: str) -> bool:
    """Toggle the pinned flag on a conversation. Returns new pinned state."""
    conv = load_conversation(user_id, conv_id)
    if not conv:
        return False
    conv.pinned = not conv.pinned
    save_conversation(user_id, conv)
    return conv.pinned


# ── Recent conversations (for sidebar) ───────────────────────

def get_recent_conversations(
    user_id: str,
    limit: int = 10,
) -> list[Conversation]:
    """
    Return the most recently updated non-deleted conversations,
    with pinned ones always at the top.
    """
    all_convs = load_all_conversations(user_id)
    active = [
        c for c in all_convs.values()
        if c.status != ConversationStatus.DELETED and c.message_count > 0
    ]
    # Pinned first, then by updated_at
    active.sort(key=lambda c: (not c.pinned, c.updated_at), reverse=True)
    return active[:limit]


# ── Search ────────────────────────────────────────────────────

def search_conversations(
    user_id: str,
    query: str,
) -> list[Conversation]:
    """
    Simple keyword search across conversation titles and message content.
    Returns matches sorted by relevance (title match first).
    """
    query_lower = query.strip().lower()
    if not query_lower:
        return []

    all_convs = load_all_conversations(user_id)
    results: list[tuple[int, Conversation]] = []

    for conv in all_convs.values():
        if conv.status == ConversationStatus.DELETED:
            continue
        score = 0
        if query_lower in conv.title.lower():
            score += 10
        for msg in conv.messages:
            if query_lower in msg.content.lower():
                score += 1
        if score > 0:
            results.append((score, conv))

    results.sort(key=lambda x: x[0], reverse=True)
    return [conv for _, conv in results]


# ── Export ────────────────────────────────────────────────────

def export_conversation_markdown(conversation: Conversation) -> str:
    """
    Render a conversation as a Markdown string suitable for download.
    """
    from utils.formatters import format_datetime
    lines = [
        f"# {conversation.title}",
        f"*Exported from Money Matters on {format_datetime(datetime.now(timezone.utc))}*",
        "",
    ]
    for msg in conversation.messages:
        role_label = "**You**" if msg.role == "user" else "**Money Matters AI**"
        ts = format_datetime(msg.timestamp) if msg.timestamp else ""
        lines.append(f"{role_label}  _{ts}_")
        lines.append("")
        lines.append(msg.content)
        if msg.sources:
            lines.append("")
            lines.append(f"*Sources: {', '.join(msg.sources)}*")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


__all__ = [
    "save_conversation",
    "load_conversation",
    "load_all_conversations",
    "delete_conversation",
    "update_conversation_title",
    "toggle_pin",
    "get_recent_conversations",
    "search_conversations",
    "export_conversation_markdown",
]
