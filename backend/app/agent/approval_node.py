from app.agent.state import (
    SupportAgentState,
)

from app.db.session import (
    SessionLocal,
)

from app.services.approval_service import (
    create_pending_approval,
)


def prepare_human_approval(
    state: SupportAgentState,
) -> dict:

    guardrail = (
        state.get(
            "guardrail_decision"
        )
        or {}
    )

    proposal = (
        state.get(
            "resolution_proposal"
        )
        or {}
    )

    if state.get("evaluation_mode",False,):
    
        return {
            "approval_request": {}
            }

    if (
        guardrail.get(
            "status"
        )
        != "needs_human_approval"
    ):

        return {
            "approval_request": {}
        }

    action = (
        proposal.get(
            "action"
        )
    )

    reason = (
        proposal.get(
            "reason"
        )
        or (
            "Sensitive support action "
            "requires human approval."
        )
    )

    if not action:

        return {
            "approval_request": {}
        }

    with SessionLocal() as db:

        approval = (
            create_pending_approval(
                db=db,

                conversation_id=(
                    state.get(
                        "conversation_id"
                    )
                ),

                order_number=(
                    state.get(
                        "order_number"
                    )
                ),

                action=action,

                reason=reason,
            )
        )

        return {
            "approval_request": {
                "approval_code":
                    approval.approval_code,

                "action":
                    approval.action,

                "status":
                    approval.status,

                "order_number":
                    approval.order_number,
            }
        }