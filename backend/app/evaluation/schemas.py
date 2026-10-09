from pydantic import BaseModel


class EvaluationCase(
    BaseModel,
):
    case_id: str

    name: str

    query: str

    expected_route: str

    required_tools: list[str]

    expected_knowledge_sufficient: bool | None = None

    expected_resolution_action: str | None = None

    expected_guardrail_status: str | None = None

    expects_citations: bool = False


class EvaluationRun(
    BaseModel,
):
    case_id: str

    query: str

    expected_route: str

    actual_route: str | None

    required_tools: list[str]

    actual_tools: list[str]

    expected_knowledge_sufficient: bool | None

    actual_knowledge_sufficient: bool | None

    expected_resolution_action: str | None

    actual_resolution_action: str | None

    expected_guardrail_status: str | None

    actual_guardrail_status: str | None

    expects_citations: bool

    citation_ids: list[str]

    final_answer: str | None

    latency_ms: float

    error: str | None


class EvaluationScore(
    BaseModel,
):
    case_id: str

    route_pass: bool

    tools_pass: bool

    knowledge_pass: bool | None

    resolution_pass: bool | None

    guardrail_pass: bool | None

    citation_pass: bool

    no_error_pass: bool

    overall_pass: bool

    passed_checks: int

    total_checks: int

    score_percent: float


class EvaluationMetrics(
    BaseModel,
):
    total_cases: int

    passed_cases: int

    failed_cases: int

    overall_pass_rate: float

    route_accuracy: float

    tool_selection_accuracy: float

    knowledge_accuracy: float | None

    resolution_accuracy: float | None

    guardrail_accuracy: float | None

    citation_compliance_rate: float

    error_free_rate: float

    average_latency_ms: float

    median_latency_ms: float

class BenchmarkResult(
    BaseModel,
):
    metrics: EvaluationMetrics

    runs: list[EvaluationRun]

    scores: list[EvaluationScore]

    passed_case_ids: list[str]

    failed_case_ids: list[str]