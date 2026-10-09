from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.approval_request import (
    ApprovalRequest,
)


def get_approval_by_code(
    db: Session,
    approval_code: str,
) -> ApprovalRequest | None:

    statement = (
        select(
            ApprovalRequest
        )
        .where(
            ApprovalRequest.approval_code
            == approval_code
        )
    )

    return db.scalar(
        statement
    )


def get_pending_approval(
    db: Session,
    conversation_id: int | None,
    order_number: str | None,
    action: str,
) -> ApprovalRequest | None:

    statement = (
        select(
            ApprovalRequest
        )
        .where(
            ApprovalRequest.status
            == "pending"
        )
        .where(
            ApprovalRequest.action
            == action
        )
    )

    if conversation_id is not None:

        statement = (
            statement.where(
                ApprovalRequest.conversation_id
                == conversation_id
            )
        )

    if order_number is not None:

        statement = (
            statement.where(
                ApprovalRequest.order_number
                == order_number
            )
        )

    return db.scalar(
        statement
    )


def list_pending_approvals(
    db: Session,
) -> list[ApprovalRequest]:

    statement = (
        select(
            ApprovalRequest
        )
        .where(
            ApprovalRequest.status
            == "pending"
        )
        .order_by(
            ApprovalRequest.requested_at.asc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )