import re
from functools import lru_cache

from ollama import Client

from app.agent.state import (
    SupportAgentState,
)

from app.core.config import settings

import json

BUSINESS_TOOL_NAMES = {
    "get_order",
    "get_customer",
    "get_customer_orders",
    "get_shipment_status",
    "get_return_status",
    "get_ticket",
}


KNOWLEDGE_TOOL_NAME = (
    "search_company_knowledge"
)


ALL_TOOL_NAMES = (
    BUSINESS_TOOL_NAMES
    | {
        KNOWLEDGE_TOOL_NAME
    }
)

def _allowed_tools_for_route(
    route: str,
) -> set[str]:

    if route == "business":
        return set(
            BUSINESS_TOOL_NAMES
        )

    if route == "knowledge":
        return {
            KNOWLEDGE_TOOL_NAME
        }

    if route == "both":
        return set(
            ALL_TOOL_NAMES
        )

    return set()

def _parse_tool_plan(
    text: str,
    allowed_tools: set[str],
) -> tuple[list[str], str]:

    text = text.strip()

    tools_match = re.search(
        r"(?im)^\s*"
        r"TOOLS\s*:\s*"
        r"(.+?)\s*$",
        text,
    )

    reason_match = re.search(
        r"(?im)^\s*"
        r"REASON\s*:\s*"
        r"(.+?)\s*$",
        text,
    )

    selected_tools = []

    if tools_match:

        raw_tools = (
            tools_match
            .group(1)
            .split(",")
        )

        seen = set()

        for tool in raw_tools:

            name = (
                tool
                .strip()
                .lower()
            )

            if (
                name in allowed_tools
                and name not in seen
            ):
                seen.add(name)
                selected_tools.append(
                    name
                )

    reason = (
        reason_match.group(1).strip()
        if reason_match
        else "No planning reason provided."
    )

    return (
        selected_tools,
        reason,
    )

def _fallback_tool_plan(
    state: SupportAgentState,
) -> list[str]:

    route = state.get(
        "route",
        "clarify",
    )

    query = (
        state.get(
            "user_query",
            ""
        )
        .lower()
    )

    order_number = state.get(
        "order_number"
    )

    customer_code = state.get(
        "customer_code"
    )

    ticket_number = state.get(
        "ticket_number"
    )

    tools = []

    if route in {
        "business",
        "both",
    }:

        if order_number:

            tools.append(
                "get_order"
            )

            if any(
                word in query
                for word in {
                    "shipping",
                    "shipment",
                    "tracking",
                    "delivery",
                    "delivered",
                    "arrived",
                }
            ):
                tools.append(
                    "get_shipment_status"
                )

            if any(
                word in query
                for word in {
                    "return",
                    "returned",
                    "refund",
                }
            ):
                tools.append(
                    "get_return_status"
                )

        if customer_code:

            if any(
                word in query
                for word in {
                    "orders",
                    "history",
                    "purchases",
                }
            ):
                tools.append(
                    "get_customer_orders"
                )

            else:
                tools.append(
                    "get_customer"
                )

        if ticket_number:

            tools.append(
                "get_ticket"
            )

    if route in {
        "knowledge",
        "both",
    }:

        tools.append(
            KNOWLEDGE_TOOL_NAME
        )

    return list(
        dict.fromkeys(
            tools
        )
    )

@lru_cache(maxsize=1)
def get_tool_planner_client() -> Client:

    return Client(
        host=settings.ollama_base_url
    )

def plan_support_tools(
    state: SupportAgentState,
) -> dict:

    route = state.get(
        "route",
        "clarify",
    )

    allowed_tools = (
        _allowed_tools_for_route(
            route
        )
    )

    if not allowed_tools:
        return {
            "selected_tools": [],
            "tool_plan_reason":
                "No tools are required."
        }

    client = (
        get_tool_planner_client()
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

        vision_overview = {
            "issue_type":
                vision_context.get(
                    "issue_type"
                ),

            "product_hint":
                vision_context.get(
                    "product_hint"
                ),

            "observations":
                vision_context.get(
                    "observations",
                    [],
                ),

            "evidence_quality":
                vision_context.get(
                    "evidence_quality"
                ),
        }

    else:

        vision_overview = {
            "available": False
        }

    response = client.chat(
        model=settings.reasoning_model,

        messages=[
            {
                "role": "system",
                "content": """
You select READ-ONLY investigation tools
for a ShopEase customer-support agent.

Available tools:

get_order
- Fetch a specific order and its products.
- Requires an order number.

get_customer
- Fetch a customer profile.
- Requires a customer code.

get_customer_orders
- Fetch a customer's order history.
- Requires a customer code.

get_shipment_status
- Fetch shipment/tracking information.
- Requires an order number.

get_return_status
- Fetch existing return requests.
- Requires an order number.

get_ticket
- Fetch a support ticket.
- Requires a ticket number.

search_company_knowledge
- Search ShopEase policies, manuals,
  FAQs and support documentation.

Select only tools useful for investigating
the customer's current request.

For an order-specific issue, normally
include get_order so the product/order
context is known.

Do not invent identifiers.

Do not select refund, replacement,
cancellation, or write-action tools.
They do not exist yet.

Return exactly:

TOOLS: <comma-separated tool names>
REASON: <short reason>

Image evidence may help select relevant
investigation tools.

Visual observations are contextual
evidence only.

Do not treat an image as proof of policy
eligibility, refund approval, replacement
approval, or exact product identity.
"""
            },
            {
                "role": "user",
                "content": (
                    f"Route: {route}\n\n"

                    "Customer query:\n"
                    f"{state.get('user_query')}\n\n"

                    "\n\nImage evidence:\n"
                    f"{json.dumps(vision_overview)}"

                    "Known identifiers:\n"
                    f"order_number="
                    f"{state.get('order_number')}\n"
                    f"customer_code="
                    f"{state.get('customer_code')}\n"
                    f"ticket_number="
                    f"{state.get('ticket_number')}"
                ),
            },
        ],

        options={
            "temperature": 0,
        },
    )

    selected_tools, reason = (
        _parse_tool_plan(
            response.message.content
            or "",
            allowed_tools,
        )
    )

    if not selected_tools:

        selected_tools = (
            _fallback_tool_plan(
                state
            )
        )

        reason = (
            "Used deterministic fallback "
            "tool planning."
        )

    if route in {
        "knowledge",
        "both",
    }:

        if (
            KNOWLEDGE_TOOL_NAME
            not in selected_tools
        ):
            selected_tools.append(
                KNOWLEDGE_TOOL_NAME
            )


    if state.get("order_number"):

        specialized_order_tools = {
            "get_shipment_status",
            "get_return_status",
        }

        if (
            any(
                tool in selected_tools
                for tool
                in specialized_order_tools
            )
            and "get_order"
            not in selected_tools
        ):
            selected_tools.insert(
                0,
                "get_order",
            )

    return {
        "selected_tools":
            selected_tools,

        "tool_plan_reason":
            reason,
    }
    