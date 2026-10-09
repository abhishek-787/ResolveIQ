from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class AgentRunLog(Base):

    __tablename__ = "agent_run_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    run_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    run_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    case_id: Mapped[str | None] = (
        mapped_column(
            String(50),
            nullable=True,
            index=True,
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

    user_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    route: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    selected_tools: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    knowledge_sufficient: Mapped[
        bool | None
    ] = mapped_column(
        Boolean,
        nullable=True,
    )

    resolution_action: Mapped[
        str | None
    ] = mapped_column(
        String(64),
        nullable=True,
    )

    guardrail_status: Mapped[
        str | None
    ] = mapped_column(
        String(40),
        nullable=True,
    )

    citation_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    final_answer_preview: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )