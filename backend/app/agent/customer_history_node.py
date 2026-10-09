from app.agent.state import (
    SupportAgentState,
)

from app.db.session import (
    SessionLocal,
)

from app.services.customer_history import (
    build_customer_history_context,
)


def load_customer_history(
    state: SupportAgentState,
) -> dict:

    try:

        with SessionLocal() as db:

            history = (
                build_customer_history_context(
                    db=db,

                    conversation_id=(
                        state.get(
                            "conversation_id"
                        )
                    ),

                    customer_code=(
                        state.get(
                            "customer_code"
                        )
                    ),

                    order_number=(
                        state.get(
                            "order_number"
                        )
                    ),

                    ticket_number=(
                        state.get(
                            "ticket_number"
                        )
                    ),
                )
            )

    except ValueError as exc:

        return {
            "customer_history": {
                "available": False,
                "reason": str(exc),
                "customer": None,
                "orders": [],
                "returns": [],
                "tickets": [],
            }
        }

    updates = {
        "customer_history":
            history
    }

    resolved_customer_code = (
        history.get(
            "customer_code"
        )
    )

    if (
        resolved_customer_code
        and not state.get(
            "customer_code"
        )
    ):

        updates[
            "customer_code"
        ] = resolved_customer_code

    return updates