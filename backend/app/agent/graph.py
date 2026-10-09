from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agent.final_response import (
    generate_final_response,
)

from app.agent.router import (
    route_support_request,
)

from app.agent.state import (
    SupportAgentState,
)

from app.agent.tool_executor import (
    execute_tool_plan,
)

from app.agent.tools.tool_planner import (
    plan_support_tools,
)

from app.agent.customer_history_node import (
    load_customer_history,
)

from app.agent.memory_node import (
    prepare_memory_context,
)

from app.agent.resolution_planner import (
    plan_resolution,
)

from app.agent.guardrails import (
    validate_resolution,
)

from app.agent.approval_node import (
    prepare_human_approval,
)

def choose_route(
    state: SupportAgentState,
) -> str:

    return state.get(
        "route",
        "clarify",
    )


def build_support_graph():

    graph = StateGraph(
        SupportAgentState
    )

    graph.add_node(
        "router",
        route_support_request,
    )

    graph.add_node(
        "tool_planner",
        plan_support_tools,
    )

    graph.add_node(
        "tool_executor",
        execute_tool_plan,
    )

    graph.add_node(
        "final_response",
        generate_final_response,
    )

    graph.add_node(
    "customer_history",
    load_customer_history,
    )

    graph.add_node(
    "memory_context",
    prepare_memory_context,
    )

    graph.add_node(
    "resolution_planner",
    plan_resolution,
    )

    graph.add_node(
    "guardrails",
    validate_resolution,
    )

    graph.add_node(
    "human_approval",
    prepare_human_approval,
    )

    graph.add_edge(
    START,
    "memory_context",
    )

    graph.add_edge(
        "memory_context",
        "router",
    )

    graph.add_conditional_edges(
        "router",
        choose_route,
        {
            "business":
                "customer_history",

            "knowledge":
                "customer_history",

            "both":
                "customer_history",

            "clarify":
                "final_response",
        },
    )

    graph.add_edge(
    "customer_history",
    "tool_planner",
    )

    graph.add_edge(
        "tool_planner",
        "tool_executor",
    )

    graph.add_edge(
    "tool_executor",
    "resolution_planner",
    )

    graph.add_edge(
    "resolution_planner",
    "guardrails",
    )

    graph.add_edge(
    "guardrails",
    "human_approval",
    )

    graph.add_edge(
        "human_approval",
        "final_response",
    )

    graph.add_edge(
        "final_response",
        END,
    )

    return graph.compile()


support_graph = (
    build_support_graph()
)