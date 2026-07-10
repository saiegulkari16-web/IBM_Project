# =============================================================
# backend/models.py
# Pydantic data models for Money Matters.
# These are the single source of truth for all data shapes
# used across services, agents, RAG, and the frontend.
# =============================================================

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Enums ─────────────────────────────────────────────────────

class MessageRole(str, Enum):
    """Who sent a chat message."""
    USER      = "user"
    ASSISTANT = "assistant"
    SYSTEM    = "system"


class IntentType(str, Enum):
    """
    Routing intents recognised by the Agentic Router.
    Maps directly to the tool registry in agents/tools.py.
    """
    NORMAL_CHAT        = "normal_chat"
    RAG                = "rag"
    WEB_SEARCH         = "web_search"
    DEEP_DIVE          = "deep_dive"
    CALCULATOR         = "calculator"
    DAILY_BRIEF        = "daily_brief"
    GOVERNMENT_SCHEME  = "government_scheme"
    FRAUD_AWARENESS    = "fraud_awareness"
    INVESTMENT         = "investment"
    LOAN               = "loan"
    UPI_HELP           = "upi_help"
    CONSUMER_RIGHTS    = "consumer_rights"
    BANKING            = "banking"
    TAX                = "tax"


class AuthProvider(str, Enum):
    """Supported authentication providers."""
    EMAIL  = "email"
    GOOGLE = "google"


class ConversationStatus(str, Enum):
    """Lifecycle status of a conversation."""
    ACTIVE  = "active"
    SAVED   = "saved"
    DELETED = "deleted"


# ── Chat Models ───────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in a conversation."""

    id        : str          = Field(default_factory=lambda: str(uuid4()))
    role      : MessageRole
    content   : str
    timestamp : datetime     = Field(default_factory=lambda: datetime.now(timezone.utc))
    intent    : Optional[IntentType] = None     # set by router on user messages
    sources   : list[str]    = Field(default_factory=list)  # RAG source citations
    metadata  : dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty.")
        return v.strip()

    class Config:
        use_enum_values = True


class Conversation(BaseModel):
    """A full conversation session between a user and the AI."""

    id         : str      = Field(default_factory=lambda: str(uuid4()))
    user_id    : str
    title      : str      = "New Conversation"
    messages   : list[ChatMessage] = Field(default_factory=list)
    status     : ConversationStatus = ConversationStatus.ACTIVE
    created_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags       : list[str] = Field(default_factory=list)
    pinned     : bool     = False

    def add_message(self, message: ChatMessage) -> None:
        """Append a message and refresh updated_at."""
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)

    @property
    def last_message_preview(self) -> str:
        """Return a short preview of the last message for sidebar display."""
        from utils.formatters import truncate_text
        for msg in reversed(self.messages):
            if msg.role == MessageRole.USER:
                return truncate_text(msg.content, max_len=50)
        return "No messages yet"

    @property
    def message_count(self) -> int:
        return len(self.messages)

    class Config:
        use_enum_values = True


# ── User Models ───────────────────────────────────────────────

class User(BaseModel):
    """Authenticated user profile."""

    id            : str      = Field(default_factory=lambda: str(uuid4()))
    username      : str
    email         : str
    display_name  : str      = ""
    avatar_url    : Optional[str] = None
    auth_provider : AuthProvider  = AuthProvider.EMAIL
    created_at    : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login    : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active     : bool     = True
    preferences   : dict[str, Any] = Field(default_factory=dict)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        from utils.validators import validate_email
        ok, msg = validate_email(v)
        if not ok:
            raise ValueError(msg)
        return v.lower().strip()

    @property
    def first_name(self) -> str:
        """Return first word of display_name or username."""
        name = self.display_name or self.username
        return name.split()[0].capitalize()

    class Config:
        use_enum_values = True


class UserSession(BaseModel):
    """Active session stored in Streamlit session state."""

    user              : Optional[User]         = None
    is_authenticated  : bool                   = False
    current_conv_id   : Optional[str]          = None
    conversations     : dict[str, Conversation] = Field(default_factory=dict)
    ui_mode           : str                    = "home"   # home | chat | calculator | brief | saved | settings
    theme             : str                    = "light"
    sidebar_open      : bool                   = True


# ── News / Daily Brief Models ─────────────────────────────────

class NewsArticle(BaseModel):
    """A single news article for the Daily Brief."""

    id          : str     = Field(default_factory=lambda: str(uuid4()))
    title       : str
    summary     : str     = ""
    source      : str     = ""
    url         : str     = ""
    published_at: Optional[datetime] = None
    category    : str     = "finance"
    ai_summary  : str     = ""   # Generated by Granite

    @property
    def display_time(self) -> str:
        from utils.formatters import relative_time
        if self.published_at:
            return relative_time(self.published_at)
        return ""


class DailyBrief(BaseModel):
    """Container for the day's financial news brief."""

    date      : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    articles  : list[NewsArticle] = Field(default_factory=list)
    generated : bool = False

    @property
    def is_stale(self) -> bool:
        """Returns True if the brief is older than 24 hours."""
        from datetime import timedelta
        return (datetime.now(timezone.utc) - self.date) > timedelta(hours=24)


# ── RAG Models ────────────────────────────────────────────────

class DocumentChunk(BaseModel):
    """A single chunk of text retrieved from the RAG knowledge base."""

    id         : str = Field(default_factory=lambda: str(uuid4()))
    source_id  : str           # matches sources_config.json id
    source_name: str
    content    : str
    url        : str  = ""
    chunk_index: int  = 0
    score      : float = 0.0   # similarity score from retrieval

    class Config:
        use_enum_values = True


class RouterDecision(BaseModel):
    """The output produced by the Agentic Router for each user message."""

    intent        : IntentType
    confidence    : float = Field(ge=0.0, le=1.0)
    original_query: str
    rewritten_query: Optional[str] = None   # cleaned/expanded query for retrieval
    metadata      : dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


# ── Calculator Models ─────────────────────────────────────────

class CalculatorResult(BaseModel):
    """Generic output model for all calculator tools."""

    calculator_type : str
    inputs          : dict[str, Any]
    result          : dict[str, Any]
    ai_explanation  : str = ""   # filled in by Granite after calculation


__all__ = [
    "MessageRole",
    "IntentType",
    "AuthProvider",
    "ConversationStatus",
    "ChatMessage",
    "Conversation",
    "User",
    "UserSession",
    "NewsArticle",
    "DailyBrief",
    "DocumentChunk",
    "RouterDecision",
    "CalculatorResult",
]
