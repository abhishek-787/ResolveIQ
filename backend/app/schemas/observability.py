from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class AgentRunLogRead(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True
    )

    run_code: str

    run_type: str

    case_id: str | None

    conversation_id: int | None

    user_query: str

    route: str | None

    selected_tools: list[str]

    knowledge_sufficient: bool | None

    resolution_action: str | None

    guardrail_status: str | None

    citation_ids: list[str]

    latency_ms: float

    success: bool

    error_message: str | None

    final_answer_preview: str | None

    created_at: datetime