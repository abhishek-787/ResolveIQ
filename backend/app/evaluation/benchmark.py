from app.evaluation.cases import (
    EVALUATION_CASES,
)

from app.evaluation.runner import (
    run_evaluation_case,
)

from app.evaluation.scoring import (
    calculate_metrics,
    score_evaluation_run,
)

from app.evaluation.schemas import (
    BenchmarkResult,
)

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path


def run_full_benchmark(
) -> BenchmarkResult:

    runs = []
    scores = []

    total = len(
        EVALUATION_CASES
    )

    for index, case in enumerate(
        EVALUATION_CASES,
        start=1,
    ):

        print(
            f"\n[{index}/{total}] "
            f"{case.case_id} - "
            f"{case.name}"
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

        runs.append(
            run
        )

        scores.append(
            score
        )

        status = (
            "PASS"
            if score.overall_pass
            else "FAIL"
        )

        print(
            f"{status} | "
            f"{score.score_percent}% | "
            f"{run.latency_ms} ms"
        )

    metrics = (
        calculate_metrics(
            runs=runs,
            scores=scores,
        )
    )

    passed_case_ids = [
        score.case_id

        for score in scores

        if score.overall_pass
    ]

    failed_case_ids = [
        score.case_id

        for score in scores

        if not score.overall_pass
    ]

    return BenchmarkResult(
        metrics=metrics,

        runs=runs,

        scores=scores,

        passed_case_ids=(
            passed_case_ids
        ),

        failed_case_ids=(
            failed_case_ids
        ),
    )

def save_json_report(
    benchmark: BenchmarkResult,
) -> Path:

    output_dir = Path(
        "evaluation_results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    output_path = (
        output_dir
        / (
            "resolveiq_benchmark_"
            f"{timestamp}.json"
        )
    )

    output_path.write_text(
        benchmark.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    return output_path


def save_markdown_report(
    benchmark: BenchmarkResult,
) -> Path:

    output_dir = Path(
        "evaluation_results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    output_path = (
        output_dir
        / (
            "resolveiq_benchmark_"
            f"{timestamp}.md"
        )
    )

    metrics = (
        benchmark.metrics
    )

    lines = [
        "# ResolveIQ Evaluation Report",
        "",
        "## Summary",
        "",
        (
            f"- Total cases: "
            f"{metrics.total_cases}"
        ),
        (
            f"- Passed cases: "
            f"{metrics.passed_cases}"
        ),
        (
            f"- Failed cases: "
            f"{metrics.failed_cases}"
        ),
        (
            f"- Overall pass rate: "
            f"{metrics.overall_pass_rate}%"
        ),
        (
            f"- Route accuracy: "
            f"{metrics.route_accuracy}%"
        ),
        (
            f"- Tool-selection accuracy: "
            f"{metrics.tool_selection_accuracy}%"
        ),
        (
            f"- Knowledge accuracy: "
            f"{metrics.knowledge_accuracy}"
        ),
        (
            f"- Resolution accuracy: "
            f"{metrics.resolution_accuracy}"
        ),
        (
            f"- Guardrail accuracy: "
            f"{metrics.guardrail_accuracy}"
        ),
        (
            f"- Citation compliance: "
            f"{metrics.citation_compliance_rate}%"
        ),
        (
            f"- Error-free rate: "
            f"{metrics.error_free_rate}%"
        ),
        (
            f"- Average latency: "
            f"{metrics.average_latency_ms} ms"
        ),
        (
            f"- Median latency: "
            f"{metrics.median_latency_ms} ms"
        ),
        "",
        "## Case Results",
        "",
        (
            "| Case | Score | Result | "
            "Route | Tools | Knowledge | "
            "Resolution | Guardrail | "
            "Citations |"
        ),
        (
            "|---|---:|---|---|---|---|---|---|---|"
        ),
    ]

    run_by_case = {
        run.case_id: run
        for run in benchmark.runs
    }

    for score in benchmark.scores:

        run = run_by_case[
            score.case_id
        ]

        result_text = (
            "PASS"
            if score.overall_pass
            else "FAIL"
        )

        lines.append(
            (
                f"| {score.case_id} "
                f"| {score.score_percent}% "
                f"| {result_text} "
                f"| {score.route_pass} "
                f"| {score.tools_pass} "
                f"| {score.knowledge_pass} "
                f"| {score.resolution_pass} "
                f"| {score.guardrail_pass} "
                f"| {score.citation_pass} |"
            )
        )

    if benchmark.failed_case_ids:

        lines.extend(
            [
                "",
                "## Failed Cases",
                "",
            ]
        )

        for case_id in (
            benchmark.failed_case_ids
        ):

            run = run_by_case[
                case_id
            ]

            lines.append(
                f"### {case_id}"
            )

            lines.append(
                ""
            )

            lines.append(
                (
                    f"Query: "
                    f"{run.query}"
                )
            )

            lines.append(
                ""
            )

            lines.append(
                (
                    f"Expected route: "
                    f"{run.expected_route}"
                )
            )

            lines.append(
                (
                    f"Actual route: "
                    f"{run.actual_route}"
                )
            )

            lines.append(
                (
                    f"Required tools: "
                    f"{run.required_tools}"
                )
            )

            lines.append(
                (
                    f"Actual tools: "
                    f"{run.actual_tools}"
                )
            )

            lines.append(
                (
                    f"Expected resolution: "
                    f"{run.expected_resolution_action}"
                )
            )

            lines.append(
                (
                    f"Actual resolution: "
                    f"{run.actual_resolution_action}"
                )
            )

            lines.append(
                (
                    f"Error: "
                    f"{run.error}"
                )
            )

            lines.append(
                ""
            )

    output_path.write_text(
        "\n".join(
            lines
        ),
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":

    benchmark = (
        run_full_benchmark()
    )

    print(
        "\n=========================="
    )

    print(
        "FINAL METRICS"
    )

    print(
        "=========================="
    )

    print(
        benchmark.metrics
        .model_dump_json(
            indent=2
        )
    )

    if (
        benchmark.failed_case_ids
    ):

        print(
            "\nFAILED CASES:"
        )

        for case_id in (
            benchmark.failed_case_ids
        ):

            print(
                f"- {case_id}"
            )

    else:

        print(
            "\nAll benchmark "
            "cases passed."
        )

    json_path = (
        save_json_report(
            benchmark
        )
    )

    markdown_path = (
        save_markdown_report(
            benchmark
        )
    )

    print(
        "\nReports saved:"
    )

    print(
        json_path
    )

    print(
        markdown_path
    )