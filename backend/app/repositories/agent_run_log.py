from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.agent_run_log import (
    AgentRunLog,
)


def create_agent_run_log(
    db: Session,
    log: AgentRunLog,
) -> AgentRunLog:

    db.add(
        log
    )

    db.commit()

    db.refresh(
        log
    )

    return log


def list_recent_agent_runs(
    db: Session,
    limit: int = 20,
) -> list[AgentRunLog]:

    statement = (
        select(
            AgentRunLog
        )
        .order_by(
            AgentRunLog.created_at.desc()
        )
        .limit(
            limit
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def get_agent_run_by_code(
    db: Session,
    run_code: str,
) -> AgentRunLog | None:

    statement = (
        select(
            AgentRunLog
        )
        .where(
            AgentRunLog.run_code
            == run_code
        )
    )

    return db.scalar(
        statement
    )