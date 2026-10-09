from typing import Any

from pydantic import BaseModel

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import inspect as sqlalchemy_inspect

from app.models import (
    Customer,
    Order,
    OrderItem,
    Product,
    Shipment,
    ReturnRequest,
    SupportTicket,
)

from sqlalchemy import select

from app.db.session import SessionLocal

class BusinessToolResult(BaseModel):
    tool_name: str
    success: bool
    message: str
    data: Any = None

def _serialize_value(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Enum,
    ):
        return value.value

    if isinstance(
        value,
        (datetime, date),
    ):
        return value.isoformat()

    if isinstance(
        value,
        Decimal,
    ):
        return float(value)

    return value

def _model_to_dict(
    model: Any,
) -> dict:

    mapper = (
        sqlalchemy_inspect(model).mapper
    )

    return {
        attribute.key:
            _serialize_value(
                getattr(
                    model,
                    attribute.key,
                )
            )

        for attribute
        in mapper.column_attrs
    }


def get_order(
    order_number: str,
) -> BusinessToolResult:

    with SessionLocal() as db:

        order = db.scalar(
            select(Order).where(
                Order.order_number == order_number
            )
        )

        if order is None:
            return BusinessToolResult(
                tool_name="get_order",
                success=False,
                message=(
                    f"Order {order_number} "
                    "was not found."
                ),
            )

        order_items = list(
            db.scalars(
                select(OrderItem).where(
                    OrderItem.order_id == order.id
                )
            ).all()
        )

        items = []

        for item in order_items:

            product = db.get(
                Product,
                item.product_id
            )

            items.append(
                {
                    "order_item": _model_to_dict(
                        item
                    ),

                    "product":( _model_to_dict(
                        product
                    )
                    if product
                    else None
                    ),
                }
            )

        return BusinessToolResult(
                    tool_name="get_order",
                    success=True,
                    message=(
                        f"Order {order_number} found."
                    ),
                    data={
                        "order":
                            _model_to_dict(
                                order
                            ),
        
                        "items":
                            items,
                    },
                )

def get_customer(
    customer_code: str,
) -> BusinessToolResult:

    with SessionLocal() as db:

        customer = db.scalar(
            select(Customer).where(
                Customer.customer_code == customer_code
            )
        )

        if customer is None:
            return BusinessToolResult(
                tool_name="get_customer",
                success=False,
                message=(
                    f"Customer "
                    f"{customer_code} "
                    "was not found."
                ),
            )

        return BusinessToolResult(
            tool_name="get_customer",
            success=True,
            message=(
                f"Customer "
                f"{customer_code} found."
            ),
            data=_model_to_dict(
                customer
            ),
        )

def get_customer_orders(
    customer_code: str,
) -> BusinessToolResult:

    with SessionLocal() as db:

        customer = db.scalar(
            select(Customer)
            .where(
                Customer.customer_code
                == customer_code
            )
        )

        if customer is None:
            return BusinessToolResult(
                tool_name=(
                    "get_customer_orders"
                ),
                success=False,
                message=(
                    f"Customer "
                    f"{customer_code} "
                    "was not found."
                ),
            )

        orders = list(
            db.scalars(
                select(Order)
                .where(
                    Order.customer_id
                    == customer.id
                )
                .order_by(
                    Order.id.desc()
                )
            ).all()
        )

        return BusinessToolResult(
            tool_name=(
                "get_customer_orders"
            ),
            success=True,
            message=(
                f"Found {len(orders)} "
                "orders."
            ),
            data=[
                _model_to_dict(order)
                for order in orders
            ],
        )

def get_shipment_status(
    order_number: str,
) -> BusinessToolResult:

    with SessionLocal() as db:

        order = db.scalar(
            select(Order)
            .where(
                Order.order_number
                == order_number
            )
        )

        if order is None:
            return BusinessToolResult(
                tool_name=(
                    "get_shipment_status"
                ),
                success=False,
                message=(
                    f"Order {order_number} "
                    "was not found."
                ),
            )

        shipments = list(
            db.scalars(
                select(Shipment)
                .where(
                    Shipment.order_id
                    == order.id
                )
                .order_by(
                    Shipment.id.desc()
                )
            ).all()
        )

        return BusinessToolResult(
            tool_name=(
                "get_shipment_status"
            ),
            success=bool(shipments),
            message=(
                f"Found {len(shipments)} "
                "shipment record(s)."
            ),
            data=[
                _model_to_dict(
                    shipment
                )
                for shipment
                in shipments
            ],
        )

def get_return_status(
    order_number: str,
) -> BusinessToolResult:

    with SessionLocal() as db:

        order = db.scalar(
            select(Order)
            .where(
                Order.order_number
                == order_number
            )
        )

        if order is None:
            return BusinessToolResult(
                tool_name=(
                    "get_return_status"
                ),
                success=False,
                message=(
                    f"Order {order_number} "
                    "was not found."
                ),
            )

        returns = list(
            db.scalars(
                select(ReturnRequest)
                .where(
                    ReturnRequest.order_id
                    == order.id
                )
                .order_by(
                    ReturnRequest.id.desc()
                )
            ).all()
        )

        return BusinessToolResult(
            tool_name=(
                "get_return_status"
            ),
            success=bool(returns),
            message=(
                f"Found {len(returns)} "
                "return request(s)."
            ),
            data=[
                _model_to_dict(
                    return_request
                )
                for return_request in returns
            ],
        )

def get_ticket(
    ticket_number: str,
) -> BusinessToolResult:

    with SessionLocal() as db:

        ticket = db.scalar(
            select(SupportTicket)
            .where(
                SupportTicket.ticket_number
                == ticket_number
            )
        )

        if ticket is None:
            return BusinessToolResult(
                tool_name="get_ticket",
                success=False,
                message=(
                    f"Ticket "
                    f"{ticket_number} "
                    "was not found."
                ),
            )

        return BusinessToolResult(
            tool_name="get_ticket",
            success=True,
            message=(
                f"Ticket "
                f"{ticket_number} found."
            ),
            data=_model_to_dict(
                ticket
            ),
        )

    