import json
import re

from functools import lru_cache

from ollama import Client

from app.agent.state import (
    SupportAgentState,
)

from app.core.config import settings

@lru_cache(maxsize=1)
def get_final_response_client() -> Client:

    return Client(
        host=settings.ollama_base_url
    )

def _get_business_results(
    state: SupportAgentState,
) -> list[dict]:

    business_context = (
        state.get(
            "business_context"
        )
        or {}
    )

    return (
        business_context.get(
            "tool_results"
        )
        or []
    )

def _has_successful_business_data(
    state: SupportAgentState,
) -> bool:

    results = (
        _get_business_results(
            state
        )
    )

    has_tool_data = any(
        result.get("success")
        and result.get("data") is not None
        for result in results
    )

    if has_tool_data:
        return True

    customer_history = (
        state.get(
            "customer_history"
        )
        or {}
    )

    return bool(
        customer_history.get(
            "available"
        )
    )

def _format_business_context(
    state: SupportAgentState,
) -> str:

    results = (
        _get_business_results(
            state
        )
    )

    if not results:
        return (
            "No business data was retrieved."
        )

    return json.dumps(
        results,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

def _format_customer_history(
    state: SupportAgentState,
) -> str:

    customer_history = (
        state.get(
            "customer_history"
        )
        or {}
    )

    if not customer_history.get(
        "available"
    ):

        return (
            "No verified customer history "
            "is available."
        )

    return json.dumps(
        customer_history,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

def _format_vision_context(
    state: SupportAgentState,
) -> str:

    vision_context = (
        state.get(
            "vision_context"
        )
        or {}
    )

    if not vision_context.get(
        "available"
    ):

        return (
            "No usable image evidence "
            "is available."
        )

    return json.dumps(
        vision_context,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

def _get_knowledge_details(
    state: SupportAgentState,
) -> tuple[
    dict,
    list[dict],
    set[str],
]:

    knowledge_context = (
        state.get(
            "knowledge_context"
        )
        or {}
    )

    data = (
        knowledge_context.get(
            "data"
        )
        or {}
    )

    citations = (
        data.get(
            "citations"
        )
        or []
    )

    valid_ids = {
        citation["citation_id"]

        for citation in citations

        if citation.get(
            "citation_id"
        )
    }

    return (
        knowledge_context,
        citations,
        valid_ids,
    )

def _format_knowledge_context(
    state: SupportAgentState,
) -> str:

    (
        _,
        citations,
        _,
    ) = _get_knowledge_details(
        state
    )

    if not citations:
        return (
            "No verified ShopEase knowledge "
            "evidence was retrieved."
        )

    blocks = []

    for citation in citations:

        blocks.append(
            (
                f"[{citation['citation_id']}]\n"
                f"Document Type: "
                f"{citation.get('document_type')}\n"
                f"Version: "
                f"{citation.get('version_label')}\n"
                f"Section: "
                f"{citation.get('section_title')}\n"
                f"Content:\n"
                f"{citation.get('content')}"
            )
        )

    return "\n\n".join(
        blocks
    )


def _sanitize_citations(
    answer: str,
    valid_ids: set[str],
) -> str:

    def replace_match(
        match: re.Match,
    ) -> str:

        citation_id = (
            match.group(1)
        )

        if citation_id in valid_ids:
            return match.group(0)

        return ""

    return re.sub(
        r"\[(S\d+)\]",
        replace_match,
        answer,
    )


def _extract_used_citations(
    answer: str,
    valid_ids: set[str],
) -> list[str]:

    found = re.findall(
        r"\[(S\d+)\]",
        answer,
    )

    used = []

    seen = set()

    for citation_id in found:

        if (
            citation_id in valid_ids
            and citation_id not in seen
        ):
            seen.add(
                citation_id
            )

            used.append(
                citation_id
            )

    return used

def _clarification_response(
    state: SupportAgentState,
) -> dict:

    return {
        "final_answer": (
            "Could you provide a little more "
            "detail about the issue, including "
            "the relevant product or an order, "
            "customer, or ticket identifier "
            "if you have one?"
        ),

        "citations_used": [],
    }

def _missing_business_response(
    state: SupportAgentState,
) -> dict:

    has_identifier = any(
        [
            state.get(
                "order_number"
            ),

            state.get(
                "customer_code"
            ),

            state.get(
                "ticket_number"
            ),
        ]
    )

    if not has_identifier:

        answer = (
            "I need the relevant order number, "
            "customer code, or ticket number "
            "before I can check that for you."
        )

    else:

        answer = (
            "I couldn't find enough matching "
            "ShopEase account or order data to "
            "answer that confidently. Please "
            "check the identifier and try again."
        )

    return {
        "final_answer": answer,
        "citations_used": [],
    }

def _insufficient_knowledge_response(
    state: SupportAgentState,
) -> dict:

    knowledge_context = (
        state.get(
            "knowledge_context"
        )
        or {}
    )

    data = (
        knowledge_context.get(
            "data"
        )
        or {}
    )

    missing = data.get(
        "missing_information"
    )

    answer = (
        "I don't have enough verified "
        "ShopEase policy information to "
        "give you a definite answer."
    )

    if missing:

        answer += (
            " The missing information is: "
            f"{missing}."
        )

    answer += (
        " This would need additional "
        "ShopEase documentation or support "
        "review before giving a firm policy "
        "decision."
    )

    return {
        "final_answer": answer,
        "citations_used": [],
    }

def _format_resolution_proposal(
    state: SupportAgentState,
) -> str:

    proposal = (
        state.get(
            "resolution_proposal"
        )
        or {}
    )

    if not proposal:

        return (
            "No resolution proposal "
            "is available."
        )

    return json.dumps(
        proposal,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

def _format_guardrail_decision(
    state: SupportAgentState,
) -> str:

    decision = (
        state.get(
            "guardrail_decision"
        )
        or {}
    )

    if not decision:

        return (
            "No guardrail decision "
            "is available."
        )

    return json.dumps(
        decision,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

def _format_approval_request(
    state: SupportAgentState,
) -> str:

    approval = (
        state.get(
            "approval_request"
        )
        or {}
    )

    if not approval:

        return (
            "No human approval request "
            "is active."
        )

    return json.dumps(
        approval,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def generate_final_response(
    state: SupportAgentState,
) -> dict:

    route = state.get(
        "route",
        "clarify",
    )

    if route == "clarify":

        return _clarification_response(
            state
        )

    needs_business = (
        route
        in {
            "business",
            "both",
        }
    )

    needs_knowledge = (
        route
        in {
            "knowledge",
            "both",
        }
    )

    if (
        needs_business
        and not _has_successful_business_data(
            state
        )
    ):

        return _missing_business_response(
            state
        )

    (
        knowledge_context,
        _,
        valid_citation_ids,
    ) = _get_knowledge_details(
        state
    )

    knowledge_success = bool(
        knowledge_context.get(
            "success"
        )
    )

    evidence_sufficient = bool(
        knowledge_context.get(
            "evidence_sufficient"
        )
    )

    if (
        route == "knowledge"
        and (
            not knowledge_success
            or not evidence_sufficient
        )
    ):

        return (
            _insufficient_knowledge_response(
                state
            )
        )

    business_evidence = (
        _format_business_context(
            state
        )
    )

    knowledge_evidence = (
        _format_knowledge_context(
            state
        )
    )

    knowledge_data = (
        knowledge_context.get(
            "data"
        )
        or {}
    )

    missing_information = (
        knowledge_data.get(
            "missing_information"
        )
    )

    customer_history_evidence = (
    _format_customer_history(
        state
    )
    )

    if not needs_knowledge:

        knowledge_status = (
            "NOT_REQUIRED"
        )

    elif (
        knowledge_success
        and evidence_sufficient
    ):

        knowledge_status = (
            "SUFFICIENT"
        )

    else:

        knowledge_status = (
            "INSUFFICIENT"
        )

    vision_evidence = (
    _format_vision_context(
        state
    )
    )

    resolution_evidence = (
    _format_resolution_proposal(
        state
    )
    )

    guardrail_evidence = (
    _format_guardrail_decision(
        state
    )
    )

    approval_evidence = (
    _format_approval_request(
        state
    )
    )

    client = (
        get_final_response_client()
    )

    response = client.chat(
        model=settings.reasoning_model,

        messages=[
            {
                "role": "system",
                "content": """
You are ResolveIQ, a ShopEase customer
support resolution assistant.

Create ONE final customer-facing response.

GROUNDING RULES:

1. Use only the supplied BUSINESS FACTS
   and KNOWLEDGE EVIDENCE.

2. Never invent order information,
   shipment status, return status,
   customer information, ticket details,
   prices, dates, or product information.

3. Policy, eligibility, warranty,
   evidence requirement, return, refund,
   or resolution claims must come from
   KNOWLEDGE EVIDENCE.

4. When making a policy claim, cite the
   supporting source using [S1], [S2],
   etc.

5. Use only citation IDs actually present
   in the provided knowledge evidence.

6. Business database facts do not need
   [S#] citations.

7. If KNOWLEDGE STATUS is INSUFFICIENT,
   do not claim that the customer is
   eligible or ineligible for a policy
   resolution. Explain what can be
   confirmed from business data and say
   that the policy decision cannot yet be
   verified.

8. Do not claim that a refund,
   replacement, cancellation, return, or
   store credit has been created or
   executed. The current tools are
   read-only.

9. If a tool failed, do not fill in the
   missing information yourself.

10. Answer directly and naturally.
    Be concise but helpful.

15. VISION EVIDENCE contains visual
    observations from an image model.

16. You may describe clearly stated visual
    observations, but use cautious wording
    such as "the image appears to show".

17. Do not use vision evidence to prove:
    - exact product identity
    - who caused damage
    - refund eligibility
    - replacement eligibility
    - warranty eligibility

18. Product/order identity comes from
    verified BUSINESS FACTS or CUSTOMER
    HISTORY.

19. Policy conclusions must still come
    from KNOWLEDGE EVIDENCE.

20. If vision evidence is unavailable,
    continue using the other available
    evidence rather than failing the whole
    request.

RESOLUTION RULES:

- RESOLUTION PROPOSAL is only a recommended
  next support action.

- It has NOT been executed.

- Never tell the customer that a refund,
  replacement, return, cancellation, or
  store credit has already been created.

- Present the recommended next step naturally.

- Do not expose internal fields such as
  ACTION or CONFIDENCE to the customer.

- Actual authorization and execution are
  handled separately.

GUARDRAIL RULES:

- GUARDRAIL DECISION overrides the
  resolution proposal if they conflict.

- If status is blocked, do not present the
  proposed action as available.

- If status is needs_information, explain
  what additional information is needed.

- If status is needs_human_approval, explain
  that the proposed action requires review
  before it can be carried out.

- If status is allowed, you may describe the
  action as the approved next system step,
  but do not claim it has already executed.

- Never expose internal guardrail field names
  or violation codes to the customer.

HUMAN APPROVAL RULES:

- A pending approval means the sensitive
  action has NOT been executed.

- If an approval request is pending, tell
  the customer that the proposed action
  requires human review before it can be
  carried out.

- Do not tell the customer that an action
  is approved unless approval status
  explicitly says approved.

- Approval itself is not execution.

- Never expose internal approval codes
  unless the interface specifically needs
  them for an authorized support user.
    
Return only the final customer-facing
answer. Do not include analysis, routing,
tool names, or internal reasoning.
"""
            },
            {
                "role": "user",
                "content": (
                    "CUSTOMER QUESTION:\n"
                    f"{state.get('user_query')}\n\n"

                    "ROUTE:\n"
                    f"{route}\n\n"

                    "BUSINESS FACTS:\n"
                    f"{business_evidence}\n\n"

                    "KNOWLEDGE STATUS:\n"
                    f"{knowledge_status}\n\n"

                    "MISSING POLICY INFORMATION:\n"
                    f"{missing_information}\n\n"

                    "CUSTOMER HISTORY:\n"
                    f"{customer_history_evidence}\n\n"

                    "VISION EVIDENCE:\n"
                    f"{vision_evidence}\n\n"

                    "RESOLUTION PROPOSAL:\n"
                    f"{resolution_evidence}\n\n"

                    "GUARDRAIL DECISION:\n"
                    f"{guardrail_evidence}\n\n"

                    "HUMAN APPROVAL:\n"
                    f"{approval_evidence}\n\n"

                    "KNOWLEDGE EVIDENCE:\n"
                    f"{knowledge_evidence}\n\n"

                    "TOOL ERRORS:\n"
                    f"{state.get('error')}"
                ),
            },
        ],

        options={
            "temperature": 0,
        },
    )

    answer = (
        response.message.content
        or ""
    ).strip()

    if not answer:

        answer = (
            "I couldn't generate a reliable "
            "response from the available "
            "ShopEase information."
        )

    answer = _sanitize_citations(
        answer=answer,
        valid_ids=(
            valid_citation_ids
        ),
    )

    citations_used = (
        _extract_used_citations(
            answer=answer,
            valid_ids=(
                valid_citation_ids
            ),
        )
    )

    return {
        "final_answer": answer,

        "citations_used":
            citations_used,
    }

