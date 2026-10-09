from app.agent.state import (
    SupportAgentState,
)

from app.schemas.guardrails import (
    GuardrailDecision,
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


POLICY_DEPENDENT_ACTIONS = {
    "create_return_request",
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
}


BUSINESS_DEPENDENT_ACTIONS = {
    "create_return_request",
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
}


ORDER_REQUIRED_ACTIONS = {
    "create_return_request",
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
}


SENSITIVE_ACTIONS = {
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
}

def _has_business_evidence(
    state: SupportAgentState,
) -> bool:

    business_context = (
        state.get(
            "business_context"
        )
        or {}
    )

    tool_results = (
        business_context.get(
            "tool_results"
        )
        or []
    )

    has_tool_data = any(
        result.get("success")
        and result.get("data") is not None
        for result in tool_results
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

def _has_sufficient_knowledge(
    state: SupportAgentState,
) -> bool:

    knowledge_context = (
        state.get(
            "knowledge_context"
        )
        or {}
    )

    return bool(
        knowledge_context.get(
            "success"
        )
        and knowledge_context.get(
            "evidence_sufficient"
        )
    )


def _has_order_reference(
    state: SupportAgentState,
) -> bool:

    if state.get(
        "order_number"
    ):
        return True

    customer_history = (
        state.get(
            "customer_history"
        )
        or {}
    )

    current_order = (
        customer_history.get(
            "current_order"
        )
    )

    return bool(
        current_order
    )

def validate_resolution(
    state: SupportAgentState,
) -> dict:

    proposal = (
        state.get(
            "resolution_proposal"
        )
        or {}
    )

    action = (
        proposal.get(
            "action"
        )
    )

    if action not in ALLOWED_ACTIONS:

        decision = (
            GuardrailDecision(
                action=(
                    "escalate_to_human"
                ),
                status="blocked",
                can_execute_now=False,
                requires_human_approval=False,
                reason=(
                    "The proposed action is "
                    "not supported by ResolveIQ."
                ),
                violations=[
                    "unsupported_action"
                ],
            )
        )

        return {
            "guardrail_decision":
                decision.model_dump()
        }

    missing_information = (
        proposal.get(
            "missing_information"
        )
    )

    if (
    missing_information
    and action
    != "escalate_to_human"
):

        decision = (
            GuardrailDecision(
                action=action,
                status=(
                    "needs_information"
                ),
                can_execute_now=False,
                requires_human_approval=False,
                reason=(
                    "Required information is "
                    "still missing before this "
                    "resolution can proceed."
                ),
                violations=[
                    "missing_information"
                ],
            )
        )

        return {
            "guardrail_decision":
                decision.model_dump()
    }

    if (
        action
        in BUSINESS_DEPENDENT_ACTIONS
        and not _has_business_evidence(
            state
        )
    ):

        decision = (
            GuardrailDecision(
                action=action,
                status="blocked",
                can_execute_now=False,
                requires_human_approval=False,
                reason=(
                    "Verified ShopEase business "
                    "data is required for this "
                    "action."
                ),
                violations=[
                    "missing_business_evidence"
                ],
            )
        )

        return {
            "guardrail_decision":
                decision.model_dump()
        }

    if (
        action
        in ORDER_REQUIRED_ACTIONS
        and not _has_order_reference(
            state
        )
    ):

        decision = (
            GuardrailDecision(
                action=action,
                status=(
                    "needs_information"
                ),
                can_execute_now=False,
                requires_human_approval=False,
                reason=(
                    "A verified ShopEase order "
                    "is required before this "
                    "action can proceed."
                ),
                violations=[
                    "missing_order_reference"
                ],
            )
        )

        return {
            "guardrail_decision":
                decision.model_dump()
        }

    if (
        action
        in POLICY_DEPENDENT_ACTIONS
        and not _has_sufficient_knowledge(
            state
        )
    ):

        decision = (
            GuardrailDecision(
                action=action,
                status="blocked",
                can_execute_now=False,
                requires_human_approval=False,
                reason=(
                    "Verified ShopEase policy "
                    "evidence is insufficient "
                    "for this action."
                ),
                violations=[
                    "insufficient_policy_evidence"
                ],
            )
        )

        return {
            "guardrail_decision":
                decision.model_dump()
        }

    if action in SENSITIVE_ACTIONS:

        decision = (
            GuardrailDecision(
                action=action,
                status=(
                    "needs_human_approval"
                ),
                can_execute_now=False,
                requires_human_approval=True,
                reason=(
                    "The proposal passed the "
                    "available evidence checks, "
                    "but this action requires "
                    "human approval."
                ),
                violations=[],
            )
        )

        return {
            "guardrail_decision":
                decision.model_dump()
        }

    decision = (
        GuardrailDecision(
            action=action,
            status="allowed",
            can_execute_now=True,
            requires_human_approval=False,
            reason=(
                "The proposal passed the "
                "current ResolveIQ guardrails."
            ),
            violations=[],
        )
    )

    return {
        "guardrail_decision":
            decision.model_dump()
    }