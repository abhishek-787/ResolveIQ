import re

from functools import lru_cache

from ollama import Client

from app.agent.state import (
    SupportAgentState,
)

from app.core.config import settings

ORDER_PATTERN = re.compile(
    r"\bORD-\d+\b",
    re.IGNORECASE,
)

CUSTOMER_PATTERN = re.compile(
    r"\bCUST-\d+\b",
    re.IGNORECASE,
)

TICKET_PATTERN = re.compile(
    r"\bTKT-\d+\b",
    re.IGNORECASE,
)

def _extract_memory_identifiers(
    history: list[dict],
) -> dict:

    identifiers = {
        "order_number": None,
        "customer_code": None,
        "ticket_number": None,
    }

    for message in reversed(
        history
    ):

        content = (
            message.get(
                "content",
                "",
            )
            or ""
        )

        if (
            identifiers[
                "order_number"
            ]
            is None
        ):

            match = (
                ORDER_PATTERN.search(
                    content
                )
            )

            if match:

                identifiers[
                    "order_number"
                ] = (
                    match.group(0)
                    .upper()
                )

        if (
            identifiers[
                "customer_code"
            ]
            is None
        ):

            match = (
                CUSTOMER_PATTERN.search(
                    content
                )
            )

            if match:

                identifiers[
                    "customer_code"
                ] = (
                    match.group(0)
                    .upper()
                )

        if (
            identifiers[
                "ticket_number"
            ]
            is None
        ):

            match = (
                TICKET_PATTERN.search(
                    content
                )
            )

            if match:

                identifiers[
                    "ticket_number"
                ] = (
                    match.group(0)
                    .upper()
                )

        if all(
            identifiers.values()
        ):

            break

    return identifiers

@lru_cache(maxsize=1)
def get_memory_client() -> Client:

    return Client(
        host=settings.ollama_base_url
    )

def _format_history(
    history: list[dict],
) -> str:

    lines = []

    for message in history:

        sender = (
            message.get(
                "sender",
                "unknown",
            )
            .upper()
        )

        content = (
            message.get(
                "content",
                "",
            )
        )

        lines.append(
            f"{sender}: {content}"
        )

    return "\n".join(
        lines
    )

def _fallback_memory_summary(
    history: list[dict],
) -> str:

    if not history:

        return (
            "No previous conversation "
            "history is available."
        )

    recent = history[-4:]

    return " | ".join(
        (
            f"{message.get('sender')}: "
            f"{message.get('content')}"
        )

        for message in recent
    )


def _summarize_history(
    history: list[dict],
    current_query: str,
) -> str:

    if not history:

        return (
            "No previous conversation "
            "history is available."
        )

    client = (
        get_memory_client()
    )

    response = client.chat(
        model=settings.reasoning_model,

        messages=[
            {
                "role": "system",
                "content": """
You summarize previous ShopEase support
conversation context for another AI agent.

Preserve useful context such as:
- relevant order/customer/ticket identifiers
- product being discussed
- customer's reported problem
- previous questions
- unresolved support issue
- policy topic being discussed

Do not invent facts.

Do not treat an earlier AI response as
authoritative database or policy evidence.
It is conversation context only.

Keep the summary concise.

Return exactly:

SUMMARY: <one concise paragraph>
"""
            },
            {
                "role": "user",
                "content": (
                    "PREVIOUS CONVERSATION:\n"
                    f"{_format_history(history)}"
                    "\n\nCURRENT CUSTOMER MESSAGE:\n"
                    f"{current_query}"
                ),
            },
        ],

        options={
            "temperature": 0,
        },
    )

    text = (
        response.message.content
        or ""
    ).strip()

    match = re.search(
        r"(?is)"
        r"SUMMARY\s*:\s*(.+)",
        text,
    )

    if not match:

        return (
            _fallback_memory_summary(
                history
            )
        )

    summary = (
        match.group(1)
        .strip()
    )

    if not summary:

        return (
            _fallback_memory_summary(
                history
            )
        )

    return summary


def prepare_memory_context(
    state: SupportAgentState,
) -> dict:

    history = (
        state.get(
            "conversation_history"
        )
        or []
    )

    identifiers = (
        _extract_memory_identifiers(
            history
        )
    )

    summary = (
        _summarize_history(
            history=history,

            current_query=(
                state.get(
                    "user_query",
                    "",
                )
            ),
        )
    )

    return {
        "memory_summary":
            summary,

        "memory_identifiers":
            identifiers,
    }