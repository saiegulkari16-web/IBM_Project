# backend package
# Re-exports the most commonly used backend symbols.

from backend.models import (
    MessageRole,
    IntentType,
    AuthProvider,
    ConversationStatus,
    ChatMessage,
    Conversation,
    User,
    UserSession,
    NewsArticle,
    DailyBrief,
    DocumentChunk,
    RouterDecision,
    CalculatorResult,
)
from backend.session import (
    init_session,
    login_user,
    logout_user,
    get_current_user,
    is_authenticated,
    set_ui_mode,
    get_ui_mode,
    new_conversation,
    get_current_conversation,
    set_current_conversation,
    add_message_to_current,
    get_conversation_list,
    delete_conversation,
    set_toast,
    pop_toast,
    set_pdf_context,
    get_pdf_context,
    clear_pdf_context,
)

__all__ = [
    # models
    "MessageRole", "IntentType", "AuthProvider", "ConversationStatus",
    "ChatMessage", "Conversation", "User", "UserSession",
    "NewsArticle", "DailyBrief", "DocumentChunk", "RouterDecision", "CalculatorResult",
    # session
    "init_session", "login_user", "logout_user",
    "get_current_user", "is_authenticated",
    "set_ui_mode", "get_ui_mode",
    "new_conversation", "get_current_conversation", "set_current_conversation",
    "add_message_to_current", "get_conversation_list", "delete_conversation",
    "set_toast", "pop_toast",
    "set_pdf_context", "get_pdf_context", "clear_pdf_context",
]
