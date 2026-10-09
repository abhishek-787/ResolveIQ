from app.agent.state import (
    SupportAgentState,
)

from app.agent.tools.business_tools import (
    BusinessToolResult,
    get_customer,
    get_customer_orders,
    get_order,
    get_return_status,
    get_shipment_status,
    get_ticket,
)

def collect_business_context(
    state: SupportAgentState,
) -> dict:

    query = (
        state["user_query"]
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

    tool_results: list[
        BusinessToolResult
    ] = []

    if order_number:

        tool_results.append(
            get_order(
                order_number
            )
        )

        shipment_keywords = {
            "shipment",
            "shipping",
            "tracking",
            "delivery",
            "delivered",
            "arrived",
        }

        if any(
            keyword in query
            for keyword
            in shipment_keywords
        ):
            tool_results.append(
                get_shipment_status(
                    order_number
                )
            )

        return_keywords = {
            "return",
            "refund",
            "returned",
        }

        if any(
            keyword in query
            for keyword
            in return_keywords
        ):
            tool_results.append(
                get_return_status(
                    order_number
                )
            )

    if customer_code:

        customer_history_keywords = {
            "orders",
            "history",
            "previous orders",
            "purchases",
        }

        if any(
            keyword in query
            for keyword
            in customer_history_keywords
        ):
            tool_results.append(
                get_customer_orders(
                    customer_code
                )
            )

        else:
            tool_results.append(
                get_customer(
                    customer_code
                )
            )

    if ticket_number:

        tool_results.append(
            get_ticket(
                ticket_number
            )
        )

    if not tool_results:

        return {
            "business_context": {
                "tool_results": [],
            },

            "error": (
                "Business data was "
                "requested, but no usable "
                "business identifier was "
                "provided."
            ),
        }

    return {
        "business_context": {
            "tool_results": [
                result.model_dump()
                for result
                in tool_results
            ],
        }
    }