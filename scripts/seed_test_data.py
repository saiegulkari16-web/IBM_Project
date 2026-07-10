#!/usr/bin/env python3
# =============================================================
# scripts/seed_test_data.py
# Seed test users and sample conversations for development.
#
# Usage:
#   python scripts/seed_test_data.py
#
# Creates:
#   • 1 demo user   (demo@moneymatters.ai / Demo@1234)
#   • 3 sample conversations with realistic messages
# =============================================================

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.auth_backend import register_user, AuthError
from backend.models import Conversation, ChatMessage, MessageRole
from backend.history import save_conversation
from utils.logger import logger


_DEMO_EMAIL    = "demo@moneymatters.ai"
_DEMO_PASSWORD = "Demo@1234"
_DEMO_USERNAME = "demo_user"
_DEMO_NAME     = "Demo User"


def seed_user():
    """Create (or skip if exists) the demo user."""
    try:
        user = register_user(
            username     = _DEMO_USERNAME,
            email        = _DEMO_EMAIL,
            password     = _DEMO_PASSWORD,
            display_name = _DEMO_NAME,
        )
        logger.info("Demo user created: {} / {}", _DEMO_EMAIL, _DEMO_PASSWORD)
        return user
    except AuthError as exc:
        if "already exists" in str(exc):
            logger.info("Demo user already exists. Fetching...")
            from backend.auth_backend import login_with_email
            return login_with_email(_DEMO_EMAIL, _DEMO_PASSWORD)
        raise


def seed_conversations(user_id: str):
    """Create 3 sample conversations."""

    now = datetime.now(timezone.utc)

    samples = [
        {
            "title"   : "SIP vs Lump Sum",
            "messages": [
                ("user",      "What is the difference between SIP and Lump Sum investment?"),
                ("assistant", "Great question! **SIP (Systematic Investment Plan)** and **Lump Sum** are two ways to invest in mutual funds:\n\n**SIP:**\n- Invest a fixed amount every month (e.g. ₹5,000/month)\n- Rupee cost averaging — you buy more units when price is low\n- Disciplined, suitable for salaried investors\n\n**Lump Sum:**\n- Invest a large amount at once\n- Better when markets are at a low point\n- Requires market timing skills\n\n*For most retail investors, SIP is recommended as it removes the guesswork of timing the market.*"),
                ("user",      "Which one gives better returns over 10 years?"),
                ("assistant", "Over 10 years, both can give similar returns if the market is not timed well. However, **SIP tends to outperform** in volatile markets because of rupee cost averaging. Studies show that a ₹5,000/month SIP at 12% p.a. over 10 years yields **₹11.6 lakh** on a total investment of **₹6 lakh** — a 93% gain. A lump sum of ₹6 lakh at the same rate gives **₹18.6 lakh**, but this assumes you invest at the perfect time. *Recommendation: Start a SIP today rather than waiting to invest a lump sum.*"),
            ],
            "offset_hours": 2,
        },
        {
            "title"   : "Income Tax FY 2024-25",
            "messages": [
                ("user",      "I earn ₹12 lakh per year. Should I choose old or new tax regime?"),
                ("assistant", "At ₹12 lakh annual income, the **New Tax Regime is generally better** for FY 2024-25. Here's a quick comparison:\n\n| | Old Regime | New Regime |\n|---|---|---|\n| Standard Deduction | ₹50,000 | ₹75,000 |\n| 80C Deduction | ₹1.5 lakh | Not available |\n| Tax Payable | ~₹83,200 | **~₹52,500** |\n\nThe new regime wins unless you have very high deductions (80C + HRA + 80D together > ₹3.5 lakh).\n\n*Source: Income Tax India, Finance Act 2024*"),
            ],
            "offset_hours": 26,
        },
        {
            "title"   : "PPF vs ELSS — Tax Saving",
            "messages": [
                ("user",      "PPF vs ELSS for tax saving under 80C — which is better?"),
                ("assistant", "Both PPF and ELSS qualify for **₹1.5 lakh deduction under Section 80C**. Here's the comparison:\n\n**PPF:**\n- Safe, government-backed\n- 7.1% guaranteed return\n- 15-year lock-in\n- EEE — fully tax-free\n\n**ELSS (Equity Linked Savings Scheme):**\n- Market-linked (historical ~12–15% p.a.)\n- Only 3-year lock-in (shortest among 80C instruments)\n- Long-term capital gains taxed at 10% above ₹1 lakh\n\n**Verdict:** If you can handle market risk and have a 5+ year horizon, **ELSS wins** on returns. If you want guaranteed, risk-free savings, **PPF is better**. Many advisors suggest a mix of both.\n\n*Source: SEBI Investor Education, AMFI*"),
            ],
            "offset_hours": 50,
        },
    ]

    for sample in samples:
        msgs = [
            ChatMessage(
                role      = MessageRole.USER if role == "user" else MessageRole.ASSISTANT,
                content   = content,
                timestamp = now - timedelta(hours=sample["offset_hours"]),
            )
            for role, content in sample["messages"]
        ]

        conv = Conversation(
            user_id    = user_id,
            title      = sample["title"],
            messages   = msgs,
            updated_at = now - timedelta(hours=sample["offset_hours"]),
        )
        save_conversation(user_id, conv)
        logger.info("Seeded conversation: '{}'", sample["title"])


def main():
    logger.info("Seeding test data...")
    user = seed_user()
    seed_conversations(user.id)
    logger.info("✅ Done. Login with: {} / {}", _DEMO_EMAIL, _DEMO_PASSWORD)


if __name__ == "__main__":
    main()
