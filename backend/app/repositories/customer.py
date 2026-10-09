from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
)

from app.models.customer import (
    Customer,
)
from app.models.order import (
    Order,
)


def get_customer_by_code(
        db:Session,
        customer_code:str
) -> Customer | None :
    statement = (select(Customer).where(Customer.customer_code == customer_code))
    return db.scalar(
        statement
    )

def get_customer_orders(
        db:Session,
        customer_id:int,
)-> list[Order]:
    statement = (select(Order).where(Order.customer_id == customer_id).order_by(Order.ordered_at.desc()))
    return list(
        db.scalars(
            statement
        )
    )