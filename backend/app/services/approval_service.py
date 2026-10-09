from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.approval_request import (
    ApprovalRequest,
)

from app.repositories.approval import (
    get_approval_by_code,
    get_pending_approval,
)


def create_pending_approval(
    db: Session,
    conversation_id: int | None,
    order_number: str | None,
    action: str,
    reason: str,
) -> ApprovalRequest:

    existing = (
        get_pending_approval(
            db=db,
            conversation_id=(
                conversation_id
            ),
            order_number=(
                order_number
            ),
            action=action,
        )
    )

    if existing is not None:

        return existing

    approval = ApprovalRequest(
        approval_code=(
            "APR-"
            + uuid4().hex[:8].upper()
        ),

        conversation_id=(
            conversation_id
        ),

        order_number=(
            order_number
        ),

        action=action,

        status="pending",

        reason=reason,

        requested_at=(
            datetime.now(
                timezone.utc
            )
        ),
    )

    db.add(
        approval
    )

    db.commit()

    db.refresh(
        approval
    )

    return approval

def approve_request(
    db: Session,
    approval_code: str,
    reviewed_by: str,
    note: str | None = None,
) -> ApprovalRequest:

    approval = (
        get_approval_by_code(
            db=db,
            approval_code=(
                approval_code
            ),
        )
    )

    if approval is None:
        raise ValueError(
            "Approval request not found."
        )

    if approval.status != "pending":
        raise ValueError(
            "Approval request has already "
            "been reviewed."
        )

    approval.status = "approved"

    approval.reviewed_by = (
        reviewed_by
    )

    approval.review_note = note

    approval.reviewed_at = (
        datetime.now(
            timezone.utc
        )
    )

    db.commit()

    db.refresh(
        approval
    )

    return approval

def reject_request(
    db: Session,
    approval_code: str,
    reviewed_by: str,
    note: str | None = None,
) -> ApprovalRequest:

    approval = (
        get_approval_by_code(
            db=db,
            approval_code=(
                approval_code
            ),
        )
    )

    if approval is None:

        raise ValueError(
            "Approval request not found."
        )

    if approval.status != "pending":

        raise ValueError(
            "Approval request has already "
            "been reviewed."
        )

    approval.status = "rejected"

    approval.reviewed_by = (
        reviewed_by
    )

    approval.review_note = note

    approval.reviewed_at = (
        datetime.now(
            timezone.utc
        )
    )

    db.commit()

    db.refresh(
        approval
    )

    return approval