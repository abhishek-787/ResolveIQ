import logging

from datetime import (
    datetime,
    timezone,
)

from time import perf_counter

from uuid import uuid4

from app.agent.graph import (
    support_graph,
)

from app.db.session import (
    SessionLocal,
)

from app.models.agent_run_log import (
    AgentRunLog,
)

from app.repositories.agent_run_log import (
    create_agent_run_log,
)


logger = logging.getLogger(
    __name__
)

def _save_run_log(
    input_state: dict,
    result: dict,
    latency_ms: float,
    run_type: str,
    case_id: str | None,
    error_message: str | None,
) -> None:

    knowledge_context = (
        result.get(
            "knowledge_context"
        )
        or {}
    )

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

    final_answer = (
        result.get(
            "final_answer"
        )
        or ""
    )

    log = AgentRunLog(
        run_code=(
            "RUN-"
            + uuid4().hex[:8].upper()
        ),

        run_type=run_type,

        case_id=case_id,

        conversation_id=(
            input_state.get(
                "conversation_id"
            )
        ),

        user_query=(
            input_state.get(
                "user_query"
            )
            or ""
        ),

        route=(
            result.get(
                "route"
            )
        ),

        selected_tools=(
            result.get(
                "selected_tools"
            )
            or []
        ),

        knowledge_sufficient=(
            knowledge_context.get(
                "evidence_sufficient"
            )
        ),

        resolution_action=(
            resolution.get(
                "action"
            )
        ),

        guardrail_status=(
            guardrail.get(
                "status"
            )
        ),

        citation_ids=(
            result.get(
                "citations_used"
            )
            or []
        ),

        latency_ms=round(
            latency_ms,
            2,
        ),

        success=(
            error_message is None
        ),

        error_message=(
            error_message
        ),

        final_answer_preview=(
            final_answer[:1000]
            if final_answer
            else None
        ),

        created_at=(
            datetime.now(
                timezone.utc
            )
        ),
    )

    try:

        with SessionLocal() as db:

            create_agent_run_log(
                db=db,
                log=log,
            )

    except Exception as exc:

        logger.warning(
            "Failed to save "
            "observability log: %s",
            exc,
        )

def invoke_support_graph_observed(
    input_state: dict,
    run_type: str = "support",
    case_id: str | None = None,
) -> tuple[dict, float]:

    started_at = (
        perf_counter()
    )

    try:

        result = (
            support_graph.invoke(
                input_state
            )
        )

    except Exception as exc:

        latency_ms = (
            perf_counter()
            - started_at
        ) * 1000

        _save_run_log(
            input_state=input_state,
            result={},
            latency_ms=latency_ms,
            run_type=run_type,
            case_id=case_id,
            error_message=str(exc),
        )

        raise

    latency_ms = (
        perf_counter()
        - started_at
    ) * 1000

    _save_run_log(
        input_state=input_state,
        result=result,
        latency_ms=latency_ms,
        run_type=run_type,
        case_id=case_id,
        error_message=None,
    )

    return (
        result,
        round(
            latency_ms,
            2,
        ),
    )