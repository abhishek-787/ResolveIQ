from time import perf_counter

from app.services.observability import (
    invoke_support_graph_observed,
)

from app.evaluation.schemas import (
    EvaluationCase,
    EvaluationRun,
)

from app.evaluation.scoring import (
    calculate_metrics,
    score_evaluation_run,
)

def run_evaluation_case(
    case: EvaluationCase,
) -> EvaluationRun:

    started_at = perf_counter()

    try:

        input_state = {
                "user_query":
                    case.query,

                "conversation_id":
                    None,

                "conversation_history":
                    [],

                "vision_context":
                    {},
                    
                "evaluation_mode": True,
            }

        result, latency_ms = (
    invoke_support_graph_observed(
        input_state=input_state,
        run_type="evaluation",
        case_id=case.case_id,
    )
)

        knowledge_context = (
            result.get(
                "knowledge_context"
            )
            or {}
        )

        knowledge_data = (
            knowledge_context.get(
                "data"
            )
            or {}
        )

        citations = (
            knowledge_data.get(
                "citations"
            )
            or []
        )

        citation_ids = [
            citation.get(
                "citation_id"
            )

            for citation in citations

            if citation.get(
                "citation_id"
            )
        ]

        resolution = (
            result.get(
                "resolution_proposal"
            )
            or {}
        )

        guardrail = (
            result.get(
                "guardrail_decision"
            )
            or {}
        )

        return EvaluationRun(
            case_id=case.case_id,

            query=case.query,

            expected_route=(
                case.expected_route
            ),

            actual_route=(
                result.get(
                    "route"
                )
            ),

            required_tools=(
                case.required_tools
            ),

            actual_tools=(
                result.get(
                    "selected_tools"
                )
                or []
            ),

            expected_knowledge_sufficient=(
                case
                .expected_knowledge_sufficient
            ),

            actual_knowledge_sufficient=(
                knowledge_context.get(
                    "evidence_sufficient"
                )
                if knowledge_context
                else None
            ),

            expected_resolution_action=(
                case
                .expected_resolution_action
            ),

            actual_resolution_action=(
                resolution.get(
                    "action"
                )
            ),

            expected_guardrail_status=(
                case
                .expected_guardrail_status
            ),

            actual_guardrail_status=(
                guardrail.get(
                    "status"
                )
            ),

            expects_citations=(
                case.expects_citations
            ),

            citation_ids=(
                citation_ids
            ),

            final_answer=(
                result.get(
                    "final_answer"
                )
            ),

            latency_ms=round(
                latency_ms,
                2,
            ),

            error=(
                result.get(
                    "error"
                )
            ),
        )

    except Exception as exc:

        latency_ms = (
            perf_counter()
            - started_at
        ) * 1000

        return EvaluationRun(
            case_id=case.case_id,

            query=case.query,

            expected_route=(
                case.expected_route
            ),

            actual_route=None,

            required_tools=(
                case.required_tools
            ),

            actual_tools=[],

            expected_knowledge_sufficient=(
                case
                .expected_knowledge_sufficient
            ),

            actual_knowledge_sufficient=None,

            expected_resolution_action=(
                case
                .expected_resolution_action
            ),

            actual_resolution_action=None,

            expected_guardrail_status=(
                case
                .expected_guardrail_status
            ),

            actual_guardrail_status=None,

            expects_citations=(
                case.expects_citations
            ),

            citation_ids=[],

            final_answer=None,

            latency_ms=round(
                latency_ms,
                2,
            ),

            error=str(exc),
        )


if __name__ == "__main__":

    from app.evaluation.cases import (
        EVALUATION_CASES,
    )

    case = (
        EVALUATION_CASES[0]
    )

    run = (
        run_evaluation_case(
            case
        )
    )

    score = (
        score_evaluation_run(
            run
        )
    )

    metrics = (
    calculate_metrics(
        runs=[
            run
        ],
        scores=[
            score
        ],
    )
)

    

    print(
        "RUN:"
    )

    print(
        run.model_dump_json(
            indent=2
        )
    )

    print(
        "\nSCORE:"
    )

    print(
        score.model_dump_json(
            indent=2
        )
    )

    print(
            "\nMETRICS:"
        )
    
    print(
            metrics.model_dump_json(
                indent=2
            )
        )