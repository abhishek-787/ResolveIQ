from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.action_execution import (
    ActionExecution,
)


def get_execution_by_approval_id(
    db: Session,
    approval_request_id: int,
) -> ActionExecution | None:

    statement = (
        select(
            ActionExecution
        )
        .where(
            ActionExecution.approval_request_id
            == approval_request_id
        )
    )

    return db.scalar(
        statement
    )


def get_execution_by_code(
    db: Session,
    execution_code: str,
) -> ActionExecution | None:

    statement = (
        select(
            ActionExecution
        )
        .where(
            ActionExecution.execution_code
            == execution_code
        )
    )

    return db.scalar(
        statement
    )