from app.evaluation.schemas import (
    EvaluationMetrics,
    EvaluationRun,
    EvaluationScore,
)

from statistics import (
    mean,
    median,
)

def _score_tools(
    required_tools: list[str],
    actual_tools: list[str],
) -> bool:

    required = set(
        required_tools
    )

    actual = set(
        actual_tools
    )

    return required.issubset(
        actual
    )

def _score_citations(
    run: EvaluationRun,
) -> bool:

    has_citations = bool(
        run.citation_ids
    )

    if run.expects_citations:

        return has_citations

    return True

def score_evaluation_run(
    run: EvaluationRun,
) -> EvaluationScore:

    route_pass = (
        run.actual_route
        == run.expected_route
    )

    tools_pass = (
        _score_tools(
            required_tools=(
                run.required_tools
            ),
            actual_tools=(
                run.actual_tools
            ),
        )
    )

    if (
        run.expected_knowledge_sufficient
        is None
    ):

        knowledge_pass = None

    else:

        knowledge_pass = (
            run.actual_knowledge_sufficient
            == run.expected_knowledge_sufficient
        )

    if (
        run.expected_resolution_action
        is None
    ):

        resolution_pass = None

    else:

        resolution_pass = (
            run.actual_resolution_action
            == run.expected_resolution_action
        )

    if (
        run.expected_guardrail_status
        is None
    ):

        guardrail_pass = None

    else:

        guardrail_pass = (
            run.actual_guardrail_status
            == run.expected_guardrail_status
        )

    citation_pass = (
        _score_citations(
            run
        )
    )

    no_error_pass = (
        run.error is None
    )

    applicable_checks = [
        route_pass,
        tools_pass,
        citation_pass,
        no_error_pass,
    ]

    if knowledge_pass is not None:

        applicable_checks.append(
            knowledge_pass
        )

    if resolution_pass is not None:

        applicable_checks.append(
            resolution_pass
        )

    if guardrail_pass is not None:

        applicable_checks.append(
            guardrail_pass
        )

    passed_checks = sum(
        1
        for check in applicable_checks
        if check
    )

    total_checks = len(
        applicable_checks
    )

    score_percent = (
        (
            passed_checks
            / total_checks
        )
        * 100
        if total_checks
        else 0.0
    )

    overall_pass = all(
        applicable_checks
    )

    return EvaluationScore(
        case_id=run.case_id,

        route_pass=route_pass,

        tools_pass=tools_pass,

        knowledge_pass=(
            knowledge_pass
        ),

        resolution_pass=(
            resolution_pass
        ),

        guardrail_pass=(
            guardrail_pass
        ),

        citation_pass=(
            citation_pass
        ),

        no_error_pass=(
            no_error_pass
        ),

        overall_pass=(
            overall_pass
        ),

        passed_checks=(
            passed_checks
        ),

        total_checks=(
            total_checks
        ),

        score_percent=round(
            score_percent,
            2,
        ),
    )


def _percentage(
    passed: int,
    total: int,
) -> float | None:

    if total == 0:
        return None

    return round(
        (
            passed
            / total
        )
        * 100,
        2,
    )

def calculate_metrics(
    runs: list[EvaluationRun],
    scores: list[EvaluationScore],
) -> EvaluationMetrics:

    if not runs:

        return EvaluationMetrics(
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            overall_pass_rate=0.0,
            route_accuracy=0.0,
            tool_selection_accuracy=0.0,
            knowledge_accuracy=None,
            resolution_accuracy=None,
            guardrail_accuracy=None,
            citation_compliance_rate=0.0,
            error_free_rate=0.0,
            average_latency_ms=0.0,
            median_latency_ms=0.0,
        )

    total_cases = len(
        scores
    )

    passed_cases = sum(
        1
        for score in scores
        if score.overall_pass
    )

    failed_cases = (
        total_cases
        - passed_cases
    )

    route_passes = sum(
        1
        for score in scores
        if score.route_pass
    )

    tool_passes = sum(
        1
        for score in scores
        if score.tools_pass
    )

    citation_passes = sum(
        1
        for score in scores
        if score.citation_pass
    )

    error_free_passes = sum(
        1
        for score in scores
        if score.no_error_pass
    )

    knowledge_scores = [
        score.knowledge_pass

        for score in scores

        if score.knowledge_pass
        is not None
    ]

    resolution_scores = [
        score.resolution_pass

        for score in scores

        if score.resolution_pass
        is not None
    ]

    guardrail_scores = [
        score.guardrail_pass

        for score in scores

        if score.guardrail_pass
        is not None
    ]

    latencies = [
        run.latency_ms
        for run in runs
    ]

    return EvaluationMetrics(
        total_cases=total_cases,

        passed_cases=(
            passed_cases
        ),

        failed_cases=(
            failed_cases
        ),

        overall_pass_rate=(
            _percentage(
                passed_cases,
                total_cases,
            )
            or 0.0
        ),

        route_accuracy=(
            _percentage(
                route_passes,
                total_cases,
            )
            or 0.0
        ),

        tool_selection_accuracy=(
            _percentage(
                tool_passes,
                total_cases,
            )
            or 0.0
        ),

        knowledge_accuracy=(
            _percentage(
                sum(
                    1
                    for passed
                    in knowledge_scores
                    if passed
                ),
                len(
                    knowledge_scores
                ),
            )
        ),

        resolution_accuracy=(
            _percentage(
                sum(
                    1
                    for passed
                    in resolution_scores
                    if passed
                ),
                len(
                    resolution_scores
                ),
            )
        ),

        guardrail_accuracy=(
            _percentage(
                sum(
                    1
                    for passed
                    in guardrail_scores
                    if passed
                ),
                len(
                    guardrail_scores
                ),
            )
        ),

        citation_compliance_rate=(
            _percentage(
                citation_passes,
                total_cases,
            )
            or 0.0
        ),

        error_free_rate=(
            _percentage(
                error_free_passes,
                total_cases,
            )
            or 0.0
        ),

        average_latency_ms=round(
            mean(
                latencies
            ),
            2,
        ),

        median_latency_ms=round(
            median(
                latencies
            ),
            2,
        ),
    )