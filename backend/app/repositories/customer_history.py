from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Customer,
    Order,
    ReturnRequest,
    SupportTicket,
)


def get_customer_by_code(
    db: Session,
    customer_code: str,
) -> Customer | None:

    return db.scalar(
        select(Customer)
        .where(
            Customer.customer_code
            == customer_code
        )
    )

def get_order_by_number(
    db: Session,
    order_number: str,
) -> Order | None:

    return db.scalar(
        select(Order)
        .where(
            Order.order_number
            == order_number
        )
    )

def get_ticket_by_number(
    db: Session,
    ticket_number: str,
) -> SupportTicket | None:

    return db.scalar(
        select(SupportTicket)
        .where(
            SupportTicket.ticket_number
            == ticket_number
        )
    )

def get_customer_by_id(
    db: Session,
    customer_id: int,
) -> Customer | None:

    return db.get(
        Customer,
        customer_id,
    )

def list_customer_orders(
    db: Session,
    customer_id: int,
    limit: int = 5,
) -> list[Order]:

    statement = (
        select(Order)
        .where(
            Order.customer_id
            == customer_id
        )
        .order_by(
            Order.id.desc()
        )
        .limit(limit)
    )

    return list(
        db.scalars(
            statement
        ).all()
    )

def list_customer_tickets(
    db: Session,
    customer_id: int,
    limit: int = 5,
) -> list[SupportTicket]:

    statement = (
        select(SupportTicket)
        .where(
            SupportTicket.customer_id
            == customer_id
        )
        .order_by(
            SupportTicket.id.desc()
        )
        .limit(limit)
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def list_customer_returns(
    db: Session,
    customer_id: int,
    limit: int = 5,
) -> list[ReturnRequest]:

    statement = (
        select(ReturnRequest)
        .join(
            Order,
            ReturnRequest.order_id
            == Order.id,
        )
        .where(
            Order.customer_id
            == customer_id
        )
        .order_by(
            ReturnRequest.id.desc()
        )
        .limit(limit)
    )

    return list(
        db.scalars(
            statement
        ).all()
    )