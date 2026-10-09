from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload,
)

from app.models.order import (
    Order,
    OrderItem,
)


def get_order_by_number(
    db: Session,
    order_number: str,
) -> Order | None:

    statement = (
        select(Order)
        .where(
            Order.order_number
            == order_number
        )
        .options(
            joinedload(
                Order.customer
            ),
            selectinload(
                Order.items
            ).joinedload(
                OrderItem.product
            ),
            selectinload(
                Order.shipments
            ),
            selectinload(
                Order.return_requests
            ),
        )
    )

    return db.scalar(
        statement
    )