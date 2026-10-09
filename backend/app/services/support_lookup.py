from sqlalchemy.orm import (
    Session,
)

from app.models.customer import (
    Customer,
)
from app.models.order import (
    Order,
)
from app.models.support import (
    SupportTicket,
)

from app.repositories.customer import (
    get_customer_by_code,
    get_customer_orders,
)
from app.repositories.order import (
    get_order_by_number,
)
from app.repositories.ticket import (
    get_ticket_by_number,
)


class ResourceNotFoundError(
    ValueError
):
    pass


def find_customer(
    db: Session,
    customer_code: str,
) -> Customer:

    customer = get_customer_by_code(
        db,
        customer_code,
    )

    if customer is None:
        raise ResourceNotFoundError(
            "Customer was not found."
        )

    return customer


def find_customer_orders(
    db: Session,
    customer_code: str,
) -> list[Order]:

    customer = find_customer(
        db,
        customer_code,
    )

    return get_customer_orders(
        db,
        customer.id,
    )


def find_order(
    db: Session,
    order_number: str,
) -> Order:

    order = get_order_by_number(
        db,
        order_number,
    )

    if order is None:
        raise ResourceNotFoundError(
            "Order was not found."
        )

    return order


def find_ticket(
    db: Session,
    ticket_number: str,
) -> SupportTicket:

    ticket = get_ticket_by_number(
        db,
        ticket_number,
    )

    if ticket is None:
        raise ResourceNotFoundError(
            "Support ticket was "
            "not found."
        )

    return ticket