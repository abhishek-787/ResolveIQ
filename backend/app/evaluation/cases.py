from app.evaluation.schemas import (
    EvaluationCase,
)


EVALUATION_CASES = [
    EvaluationCase(
        case_id="EVAL-001",

        name="Standard return window",

        query=(
            "What is ShopEase's "
            "standard return window?"
        ),

        expected_route="knowledge",

        required_tools=[
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=True,

        expected_resolution_action=(
            "provide_information"
        ),

        expected_guardrail_status="allowed",

        expects_citations=True,
    ),

    EvaluationCase(
        case_id="EVAL-002",

        name="Damaged monitor evidence",

        query=(
            "ORD-10482 arrived with "
            "a cracked screen. "
            "What proof do I need?"
        ),

        expected_route="both",

        required_tools=[
            "get_order",
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=True,

        expected_resolution_action=(
            "provide_information"
        ),

        expected_guardrail_status="allowed",

        expects_citations=True,
    ),

    EvaluationCase(
        case_id="EVAL-003",

        name="Order lookup",

        query=(
            "Tell me the details "
            "of ORD-10482."
        ),

        expected_route="business",

        required_tools=[
            "get_order",
        ],

        expected_knowledge_sufficient=None,

        expected_resolution_action=(
            "provide_information"
        ),

        expected_guardrail_status="allowed",

        expects_citations=False,
    ),

    EvaluationCase(
        case_id="EVAL-004",

        name="Wrong product support",

        query=(
            "ORD-10483 contains the "
            "wrong headphones. "
            "What should I do?"
        ),

        expected_route="both",

        required_tools=[
            "get_order",
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=True,

        expected_resolution_action=None,

        expected_guardrail_status=None,

        expects_citations=True,
    ),

    EvaluationCase(
        case_id="EVAL-005",

        name="Refund timing",

        query=(
            "How long does a ShopEase "
            "refund normally take?"
        ),

        expected_route="knowledge",

        required_tools=[
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=True,

        expected_resolution_action=(
            "provide_information"
        ),

        expected_guardrail_status="allowed",

        expects_citations=True,
    ),

    EvaluationCase(
        case_id="EVAL-006",

        name="Missing delivery policy",

        query=(
            "ORD-10485 says delivered "
            "but I did not receive it. "
            "What should I do?"
        ),

        expected_route="both",

        required_tools=[
            "get_order",
            "get_shipment_status",
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=False,

        expected_resolution_action=(
            "escalate_to_human"
        ),

        expected_guardrail_status="allowed",

        expects_citations=False,
    ),

    EvaluationCase(
        case_id="EVAL-007",

        name="Keyboard troubleshooting",

        query=(
            "ORD-10486 keyboard is "
            "not being detected. "
            "How do I fix it?"
        ),

        expected_route="both",

        required_tools=[
            "get_order",
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=False,

        expected_resolution_action=(
            "escalate_to_human"
        ),

        expected_guardrail_status="allowed",

        expects_citations=False,
    ),

    EvaluationCase(
        case_id="EVAL-008",

        name="Damaged monitor replacement",

        query=(
            "ORD-10482 arrived with "
            "a cracked screen. "
            "Can I get a replacement?"
        ),

        expected_route="both",

        required_tools=[
            "get_order",
            "search_company_knowledge",
        ],

        expected_knowledge_sufficient=True,

        expected_resolution_action=None,

        expected_guardrail_status=None,

        expects_citations=True,
    ),
]