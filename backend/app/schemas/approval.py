from datetime import datetime

from typing import Literal

from pydantic import BaseModel


ApprovalStatus = Literal[
    "pending",
    "approved",
    "rejected",
]


class ApprovalRequestRead(
    BaseModel,
):
    approval_code: str

    conversation_id: int | None

    order_number: str | None

    action: str

    status: ApprovalStatus

    reason: str

    requested_at: datetime

    reviewed_at: datetime | None

    reviewed_by: str | None

    review_note: str | None


class ApprovalReviewRequest(
    BaseModel,
):
    reviewed_by: str

    note: str | None = None