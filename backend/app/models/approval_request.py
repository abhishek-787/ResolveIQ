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


class ApprovalRequest(Base):

    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    approval_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
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
        default="pending",
        index=True,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    requested_at: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=False,
        )
    )

    reviewed_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )

    reviewed_by: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
        )
    )

    review_note: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )