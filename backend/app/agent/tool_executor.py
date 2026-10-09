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

from app.agent.tools.knowledge_tools import (
    search_company_knowledge,
)


def _missing_input_result(
    tool_name: str,
    field_name: str,
) -> BusinessToolResult:

    return BusinessToolResult(
        tool_name=tool_name,
        success=False,
        message=(
            f"Missing required input: "
            f"{field_name}."
        ),
        data=None,
    )


def execute_tool_plan(
    state: SupportAgentState,
) -> dict:

    selected_tools = state.get(
        "selected_tools",
        [],
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

    business_results = []

    knowledge_result = None

    errors = []

    for tool_name in selected_tools:

        if tool_name == "get_order":

            if not order_number:

                result = (
                    _missing_input_result(
                        "get_order",
                        "order_number",
                    )
                )

            else:

                result = (
                    get_order(
                        order_number
                    )
                )

            business_results.append(
                result
            )

        elif (
            tool_name
            == "get_shipment_status"
        ):

            if not order_number:

                result = (
                    _missing_input_result(
                        "get_shipment_status",
                        "order_number",
                    )
                )

            else:

                result = (
                    get_shipment_status(
                        order_number
                    )
                )

            business_results.append(
                result
            )

        elif (
            tool_name
            == "get_return_status"
        ):

            if not order_number:

                result = (
                    _missing_input_result(
                        "get_return_status",
                        "order_number",
                    )
                )

            else:

                result = (
                    get_return_status(
                        order_number
                    )
                )

            business_results.append(
                result
            )

        elif tool_name == "get_customer":

            if not customer_code:

                result = (
                    _missing_input_result(
                        "get_customer",
                        "customer_code",
                    )
                )

            else:

                result = (
                    get_customer(
                        customer_code
                    )
                )

            business_results.append(
                result
            )

        elif (
            tool_name
            == "get_customer_orders"
        ):

            if not customer_code:

                result = (
                    _missing_input_result(
                        "get_customer_orders",
                        "customer_code",
                    )
                )

            else:

                result = (
                    get_customer_orders(
                        customer_code
                    )
                )

            business_results.append(
                result
            )

        elif tool_name == "get_ticket":

            if not ticket_number:

                result = (
                    _missing_input_result(
                        "get_ticket",
                        "ticket_number",
                    )
                )

            else:

                result = (
                    get_ticket(
                        ticket_number
                    )
                )

            business_results.append(
                result
            )

        elif (
            tool_name
            == "search_company_knowledge"
        ):

            knowledge_query = (
                state["user_query"]
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

                issue_type = (
                    vision_context.get(
                        "issue_type"
                    )
                )

                observations = (
                    vision_context.get(
                        "observations"
                    )
                    or []
                )

                product_hint = (
                    vision_context.get(
                        "product_hint"
                    )
                )

                vision_parts = []

                if issue_type:

                    vision_parts.append(
                        (
                            "Visual issue: "
                            f"{issue_type}."
                        )
                    )

                if observations:

                    vision_parts.append(
                        (
                            "Visible observations: "
                            + " ".join(
                                observations
                            )
                        )
                    )

                if product_hint:

                    vision_parts.append(
                        (
                            "Visual product hint: "
                            f"{product_hint}."
                        )
                    )

                if vision_parts:

                    knowledge_query += (
                        "\n\nIMAGE CONTEXT:\n"
                        + "\n".join(
                            vision_parts
                        )
                    )

            knowledge_result = (
                search_company_knowledge(
                    knowledge_query
                )
            )

    for result in business_results:

        if not result.success:

            errors.append(
                result.message
            )

    response = {}

    if business_results:

        response[
            "business_context"
        ] = {
            "tool_results": [
                result.model_dump()
                for result
                in business_results
            ]
        }

    if knowledge_result:

        response[
            "knowledge_context"
        ] = (
            knowledge_result
            .model_dump()
        )

        if not knowledge_result.success:

            errors.append(
                knowledge_result.message
            )

    if errors:

        response["error"] = (
            " | ".join(
                errors
            )
        )

    return response