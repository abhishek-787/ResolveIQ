import json
import re

from functools import lru_cache

from ollama import Client

from app.agent.state import (
    SupportAgentState,
)

from app.core.config import (
    settings,
)

from app.schemas.resolution import (
    ResolutionProposal,
)


ALLOWED_ACTIONS = {
    "provide_information",
    "request_more_information",
    "create_return_request",
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
    "escalate_to_human",
}


VALID_CONFIDENCE = {
    "high",
    "medium",
    "low",
}

@lru_cache(maxsize=1)
def get_resolution_client() -> Client:

    return Client(
        host=settings.ollama_base_url
    )

def _extract_field(
    text: str,
    field: str,
) -> str | None:

    match = re.search(
        rf"(?im)^\s*"
        rf"{re.escape(field)}"
        rf"\s*:\s*(.+?)\s*$",
        text,
    )

    if not match:
        return None

    value = (
        match.group(1)
        .strip()
    )

    return value or None

def _parse_resolution(
    text: str,
) -> ResolutionProposal:

    action = (
        _extract_field(
            text,
            "ACTION",
        )
        or "escalate_to_human"
    ).lower()

    confidence = (
        _extract_field(
            text,
            "CONFIDENCE",
        )
        or "low"
    ).lower()

    reason = (
        _extract_field(
            text,
            "REASON",
        )
        or (
            "The available evidence was "
            "not sufficient for a more "
            "specific recommendation."
        )
    )

    missing_information = (
        _extract_field(
            text,
            "MISSING_INFORMATION",
        )
    )

    if action not in ALLOWED_ACTIONS:

        action = (
            "escalate_to_human"
        )

    if confidence not in VALID_CONFIDENCE:

        confidence = "low"

    if (
        missing_information
        and missing_information.lower()
        in {
            "none",
            "null",
            "n/a",
            "not applicable",
        }
    ):

        missing_information = None

    return ResolutionProposal(
        action=action,
        confidence=confidence,
        reason=reason,
        missing_information=(
            missing_information
        ),
    )

def _fallback_resolution(
    state: SupportAgentState,
) -> ResolutionProposal:

    route = state.get(
        "route",
        "clarify",
    )

    if route == "clarify":

        return ResolutionProposal(
            action=(
                "request_more_information"
            ),
            confidence="high",
            reason=(
                "More information is needed "
                "before a reliable resolution "
                "can be proposed."
            ),
            missing_information=(
                "Additional issue details "
                "or an identifier are needed."
            ),
        )

    knowledge_context = (
        state.get(
            "knowledge_context"
        )
        or {}
    )

    if (
        route in {
            "knowledge",
            "both",
        }
        and not knowledge_context.get(
            "evidence_sufficient"
        )
    ):

        return ResolutionProposal(
            action="escalate_to_human",
            confidence="high",
            reason=(
                "Verified ShopEase policy "
                "evidence is insufficient "
                "for a reliable resolution."
            ),
            missing_information=(
                "Additional policy evidence "
                "or human review is required."
            ),
        )

    return ResolutionProposal(
        action="provide_information",
        confidence="low",
        reason=(
            "No stronger resolution could "
            "be safely established from "
            "the available evidence."
        ),
        missing_information=None,
    )

def plan_resolution(
    state: SupportAgentState,
) -> dict:

    route = state.get(
        "route",
        "clarify",
    )

    if route == "clarify":

        proposal = (
            _fallback_resolution(
                state
            )
        )

        return {
            "resolution_proposal":
                proposal.model_dump()
        }

    knowledge_context = (
        state.get(
            "knowledge_context"
        )
        or {}
    )

    if (
        route in {
            "knowledge",
            "both",
        }
        and not knowledge_context.get(
            "evidence_sufficient"
        )
    ):

        proposal = (
            _fallback_resolution(
                state
            )
        )

        return {
            "resolution_proposal":
                proposal.model_dump()
        }

    business_context = (
        state.get(
            "business_context"
        )
        or {}
    )

    customer_history = (
        state.get(
            "customer_history"
        )
        or {}
    )

    vision_context = (
        state.get(
            "vision_context"
        )
        or {}
    )

    client = (
        get_resolution_client()
    )

    response = client.chat(
        model=settings.reasoning_model,

        messages=[
            {
                "role": "system",
                "content": """
You are the resolution planning component
of ResolveIQ for ShopEase.

Your job is to propose the safest next
customer-support action.

You NEVER execute actions.

Allowed ACTION values:

provide_information
request_more_information
create_return_request
create_replacement_request
issue_refund
issue_store_credit
cancel_order
escalate_to_human

Rules:

- Use only the supplied verified context.
- Do not invent customer or order facts.
- Do not invent policy rules.
- Policy-dependent actions must be supported
  by ShopEase knowledge evidence.
- Vision observations are supporting context,
  not proof of eligibility.
- If important information is missing, prefer
  request_more_information.
- If evidence conflicts or is insufficient,
  prefer escalate_to_human.
- Never claim an action has already happened.

Return exactly:

ACTION: <allowed action>
CONFIDENCE: high|medium|low
REASON: <short reason>
MISSING_INFORMATION: <missing information or none>
"""
            },
            {
                "role": "user",
                "content": (
                    "CUSTOMER QUESTION:\n"
                    f"{state.get('user_query')}\n\n"

                    "BUSINESS CONTEXT:\n"
                    f"{json.dumps(
                        business_context,
                        ensure_ascii=False,
                        default=str,
                    )}\n\n"

                    "CUSTOMER HISTORY:\n"
                    f"{json.dumps(
                        customer_history,
                        ensure_ascii=False,
                        default=str,
                    )}\n\n"

                    "KNOWLEDGE CONTEXT:\n"
                    f"{json.dumps(
                        knowledge_context,
                        ensure_ascii=False,
                        default=str,
                    )}\n\n"

                    "VISION CONTEXT:\n"
                    f"{json.dumps(
                        vision_context,
                        ensure_ascii=False,
                        default=str,
                    )}"
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
    ).strip()

    if not raw_text:

        proposal = (
            _fallback_resolution(
                state
            )
        )

    else:

        proposal = (
            _parse_resolution(
                raw_text
            )
        )

    return {
        "resolution_proposal":
            proposal.model_dump()
    }

