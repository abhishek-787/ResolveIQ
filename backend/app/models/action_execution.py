from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class ActionExecution(Base):

    __tablename__ = "action_executions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    execution_code: Mapped[str] = (
        mapped_column(
            String(50),
            unique=True,
            index=True,
            nullable=False,
        )
    )

    approval_request_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "approval_requests.id"
            ),
            unique=True,
            index=True,
            nullable=False,
        )
    )

    conversation_id: Mapped[int | None] = (
        mapped_column(
            ForeignKey(
                "conversations.id"
            ),
            nullable=True,
            index=True,
        )
    )

    order_number: Mapped[str | None] = (
        mapped_column(
            String(50),
            nullable=True,
            index=True,
        )
    )

    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    result_reference: Mapped[str | None] = (
        mapped_column(
            String(50),
            nullable=True,
            unique=True,
        )
    )

    result_message: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    error_message: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    executed_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=False,
        )
    )

    executed_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )