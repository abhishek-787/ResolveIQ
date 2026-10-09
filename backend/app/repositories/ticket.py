from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.support import (
    SupportTicket,
)


def get_ticket_by_number(
    db: Session,
    ticket_number: str,
) -> SupportTicket | None:

    statement = (
        select(SupportTicket)
        .where(
            SupportTicket.ticket_number
            == ticket_number
        )
        .options(
            joinedload(
                SupportTicket.customer
            ),
            joinedload(
                SupportTicket.order
            ),
        )
    )

    return db.scalar(
        statement
    )