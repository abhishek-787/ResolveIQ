from datetime import datetime

from typing import Literal

from pydantic import BaseModel


ExecutionStatus = Literal[
    "processing",
    "succeeded",
    "failed",
]


class ActionExecutionRead(
    BaseModel,
):
    execution_code: str

    approval_request_id: int

    conversation_id: int | None

    order_number: str | None

    action: str

    status: ExecutionStatus

    result_reference: str | None

    result_message: str | None

    error_message: str | None

    executed_by: str

    created_at: datetime

    executed_at: datetime | None


class ApproveAndExecuteResponse(
    BaseModel,
):
    approval_code: str

    approval_status: str

    execution: ActionExecutionRead


class AuditEvent(
    BaseModel,
):
    event_type: str

    occurred_at: datetime

    actor: str

    details: str