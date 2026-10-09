from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.models.enums import (
    IssueType,
    TicketPriority,
    TicketStatus,
)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    ticket_number: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.id"
        ),
        nullable=False,
        index=True,
    )

    order_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "orders.id"
        ),
        nullable=True,
        index=True,
    )

    issue_type: Mapped[IssueType] = mapped_column(
        SAEnum(
            IssueType,
            name="issue_type",
        ),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[TicketPriority] = mapped_column(
        SAEnum(
            TicketPriority,
            name="ticket_priority",
        ),
        nullable=False,
        default=TicketPriority.MEDIUM,
    )

    status: Mapped[TicketStatus] = mapped_column(
        SAEnum(
            TicketStatus,
            name="ticket_status",
        ),
        nullable=False,
        default=TicketStatus.OPEN,
    )

    resolution_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    customer = relationship(
        "Customer",
        back_populates="support_tickets",
    )

    order = relationship(
        "Order",
        back_populates="support_tickets",
    )

    conversations = relationship(
        "Conversation",
        back_populates="ticket",
    )