from typing import TypedDict


class SupportAgentState(
    TypedDict,
    total=False,
):
    user_query: str

    conversation_id: int | None
    conversation_history: list[dict]

    memory_summary: str
    memory_identifiers: dict

    customer_history: dict

    vision_context: dict

    resolution_proposal: dict

    guardrail_decision: dict

    approval_request: dict

    evaluation_mode: bool

    route: str
    route_reason: str

    customer_code: str | None
    order_number: str | None
    ticket_number: str | None

    needs_business_data: bool
    needs_knowledge: bool

    selected_tools: list[str]
    tool_plan_reason: str

    business_context: dict
    knowledge_context: dict

    final_answer: str | None
    citations_used: list[str]

    error: str | None