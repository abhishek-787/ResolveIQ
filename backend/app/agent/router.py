import re
from functools import lru_cache

from ollama import Client

from app.agent.state import (
    SupportAgentState,
)

import json

from app.core.config import settings


def _extract_identifiers(
    query: str,
) -> dict[str, str | None]:

    order_match = re.search(
        r"\bORD-\d+\b",
        query,
        re.IGNORECASE,
    )

    customer_match = re.search(
        r"\bCUST-\d+\b",
        query,
        re.IGNORECASE,
    )

    ticket_match = re.search(
        r"\bTKT-\d+\b",
        query,
        re.IGNORECASE,
    )

    return {
        "order_number": (
            order_match.group(0).upper()
            if order_match
            else None
        ),

        "customer_code": (
            customer_match.group(0).upper()
            if customer_match
            else None
        ),

        "ticket_number": (
            ticket_match.group(0).upper()
            if ticket_match
            else None
        ),
    }


@lru_cache(maxsize=1)
def get_router_client() -> Client:

    return Client(
        host=settings.ollama_base_url
    )


def _parse_route_response(
    text: str,
) -> tuple[str, str]:

    text = text.strip()

    route_match = re.search(
        r"(?im)^\s*"
        r"ROUTE\s*:\s*"
        r"(business|knowledge|both|clarify)"
        r"\s*$",
        text,
    )

    reason_match = re.search(
        r"(?im)^\s*"
        r"REASON\s*:\s*"
        r"(.+?)\s*$",
        text,
    )

    if not route_match:
        return (
            "clarify",
            "Routing output could not be parsed.",
        )

    route = (
        route_match
        .group(1)
        .lower()
    )

    reason = (
        reason_match.group(1).strip()
        if reason_match
        else "No routing reason provided."
    )

    return route, reason


def route_support_request(
    state: SupportAgentState,
) -> dict:

    query = (
        state["user_query"]
        .strip()
    )

    identifiers = (
        _extract_identifiers(
            query
        )
    )

    
    memory_identifiers = (
        state.get(
            "memory_identifiers"
        )
        or {}
    )

    resolved_identifiers = {
        "order_number": (
            identifiers.get(
                "order_number"
            )
            or memory_identifiers.get(
                "order_number"
            )
        ),

        "customer_code": (
            identifiers.get(
                "customer_code"
            )
            or memory_identifiers.get(
                "customer_code"
            )
        ),

        "ticket_number": (
            identifiers.get(
                "ticket_number"
            )
            or memory_identifiers.get(
                "ticket_number"
            )
        ),
    }


    memory_summary = (
        state.get(
            "memory_summary"
        )
        or (
            "No previous conversation "
            "context."
        )
    )

    client = (
        get_router_client()
    )

    vision_context = (
    state.get(
        "vision_context"
    )
    or {}
)


    if vision_context.get(
    "available"
    ):

        vision_summary = json.dumps(
            vision_context,
            ensure_ascii=False,
            default=str,
        )

    else:

        vision_summary = (
            "No usable image evidence "
            "is available."
        )

  

    response = client.chat(
        model=settings.reasoning_model,

        messages=[
            {
                "role": "system",
                "content": """
You route customer-support requests
for ShopEase.

Choose exactly one route:

business
knowledge
both
clarify


BUSINESS:
Use when the request mainly needs
structured customer-specific data such as:

- order status
- shipment status
- return status
- customer order history
- previous support history
- support ticket information


KNOWLEDGE:
Use when the request mainly asks about
ShopEase policies, rules, eligibility,
procedures, manuals, FAQs, or
troubleshooting guidance.


BOTH:
Use when answering correctly requires both
customer-specific business data AND
ShopEase policy/manual knowledge.


CLARIFY:
Use when important information is missing
or the request is too ambiguous to safely
determine what the customer needs.


CONVERSATION MEMORY RULES:

Conversation context may be used to
understand follow-up references such as:

- "it"
- "that order"
- "the monitor"
- "what proof"
- "what photos"
- "what about replacement?"
- "what issue were we discussing?"

The CURRENT customer message has priority
over previous conversation context.

If the current message contains a new
order, customer, or ticket identifier,
treat that identifier as the active one.

Do not choose BUSINESS simply because an
old order/customer/ticket identifier exists
in conversation memory.

If the current message is a generic policy
question that does not depend on a specific
customer/order/history, choose KNOWLEDGE.

If the current follow-up refers to a
specific previous order/product AND asks
about ShopEase policy, evidence,
eligibility, replacement, refund, warranty,
or procedure, choose BOTH.

If conversation memory clearly provides
the missing context for a follow-up, do not
choose CLARIFY unnecessarily.


Examples:

"What is the status of ORD-10482?"
→ business

"What is the ShopEase return window?"
→ knowledge

"ORD-10482 arrived cracked.
Can I get a replacement?"
→ both

Previous conversation:
"ORD-10482 arrived cracked."

Current message:
"What photos should I send?"
→ both

Previous conversation:
"ORD-10482 arrived cracked."

Current message:
"What is ShopEase's standard return window?"
→ knowledge

"It isn't working. What should I do?"
with no useful previous context
→ clarify

Do not answer the customer.
Do not invent facts.

Return exactly:

ROUTE: <business|knowledge|both|clarify>
REASON: <short reason>

IMAGE EVIDENCE RULES:

Image evidence may help understand what
the customer is referring to.

For example, if the customer says
"Can I replace this?" and the image shows
visible product damage, image context can
help identify the issue as damaged-product
support.

Image observations are not company policy
and do not prove refund/replacement
eligibility.

Do not infer who caused visible damage.
""",
            },
            {
                "role": "user",
                "content": (
                    "CURRENT CUSTOMER MESSAGE:\n"
                    f"{query}\n\n"

                    "PREVIOUS CONVERSATION CONTEXT:\n"
                    f"{memory_summary}\n\n"

                    "\n\nIMAGE EVIDENCE:\n"
                    f"{vision_summary}"

                    "IDENTIFIERS IN CURRENT MESSAGE:\n"
                    f"order_number="
                    f"{identifiers.get('order_number')}\n"
                    f"customer_code="
                    f"{identifiers.get('customer_code')}\n"
                    f"ticket_number="
                    f"{identifiers.get('ticket_number')}\n\n"

                    "ACTIVE IDENTIFIERS AFTER "
                    "APPLYING CONVERSATION MEMORY:\n"
                    f"order_number="
                    f"{resolved_identifiers.get('order_number')}\n"
                    f"customer_code="
                    f"{resolved_identifiers.get('customer_code')}\n"
                    f"ticket_number="
                    f"{resolved_identifiers.get('ticket_number')}"
                ),
            },
        ],

        options={
            "temperature": 0,
        },
    )

    raw_text = (
        response.message.content
        or ""
    )

    route, reason = (
        _parse_route_response(
            raw_text
        )
    )

    return {
        "route":
            route,

        "route_reason":
            reason,

        "needs_business_data": (
            route
            in {
                "business",
                "both",
            }
        ),

        "needs_knowledge": (
            route
            in {
                "knowledge",
                "both",
            }
        ),

        **resolved_identifiers,
    }