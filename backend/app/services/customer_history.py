from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session

from app.models import (
    Conversation,
)

from app.repositories.conversation import (
    get_conversation,
)

from app.repositories.customer_history import (
    get_customer_by_code,
    get_customer_by_id,
    get_order_by_number,
    get_ticket_by_number,
    list_customer_orders,
    list_customer_returns,
    list_customer_tickets,
)

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
        sqlalchemy_inspect(model)
        .mapper
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

def _resolve_customer(
    db: Session,
    conversation: Conversation | None,
    customer_code: str | None,
    order_number: str | None,
    ticket_number: str | None,
):

    resolved_customer_ids: set[int] = set()

    matched_customer = None
    matched_order = None
    matched_ticket = None

    if customer_code:

        matched_customer = (
            get_customer_by_code(
                db=db,
                customer_code=customer_code,
            )
        )

        if matched_customer is None:
            raise ValueError(
                f"Customer {customer_code} "
                "was not found."
            )

        resolved_customer_ids.add(
            matched_customer.id
        )

    if order_number:

        matched_order = (
            get_order_by_number(
                db=db,
                order_number=order_number,
            )
        )

        if matched_order is None:
            raise ValueError(
                f"Order {order_number} "
                "was not found."
            )

        resolved_customer_ids.add(
            matched_order.customer_id
        )

    if ticket_number:

        matched_ticket = (
            get_ticket_by_number(
                db=db,
                ticket_number=ticket_number,
            )
        )

        if matched_ticket is None:
            raise ValueError(
                f"Ticket {ticket_number} "
                "was not found."
            )

        if matched_ticket.customer_id:
            resolved_customer_ids.add(
                matched_ticket.customer_id
            )

    if len(resolved_customer_ids) > 1:

        raise ValueError(
            "The supplied customer, order, "
            "and ticket identifiers do not "
            "belong to the same customer."
        )

    explicit_customer_id = (
        next(
            iter(
                resolved_customer_ids
            )
        )
        if resolved_customer_ids
        else None
    )

    if (
        conversation
        and conversation.customer_id
        and explicit_customer_id
        and conversation.customer_id
        != explicit_customer_id
    ):

        raise ValueError(
            "This conversation is already "
            "linked to a different customer."
        )

    resolved_customer_id = (
        explicit_customer_id
        or (
            conversation.customer_id
            if conversation
            else None
        )
    )

    if resolved_customer_id is None:

        return (
            None,
            matched_order,
            matched_ticket,
        )

    customer = (
        get_customer_by_id(
            db=db,
            customer_id=(
                resolved_customer_id
            ),
        )
    )

    return (
        customer,
        matched_order,
        matched_ticket,
    )


def build_customer_history_context(
    db: Session,
    conversation_id: int | None,
    customer_code: str | None,
    order_number: str | None,
    ticket_number: str | None,
    history_limit: int = 5,
) -> dict:

    conversation = None

    if conversation_id is not None:

        conversation = (
            get_conversation(
                db=db,
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            raise ValueError(
                "Conversation not found."
            )

    (
        customer,
        matched_order,
        matched_ticket,
    ) = _resolve_customer(
        db=db,
        conversation=conversation,
        customer_code=customer_code,
        order_number=order_number,
        ticket_number=ticket_number,
    )

    if customer is None:

        return {
            "available": False,
            "customer": None,
            "orders": [],
            "returns": [],
            "tickets": [],
        }

    orders = list_customer_orders(
        db=db,
        customer_id=customer.id,
        limit=history_limit,
    )

    returns = list_customer_returns(
        db=db,
        customer_id=customer.id,
        limit=history_limit,
    )

    tickets = list_customer_tickets(
        db=db,
        customer_id=customer.id,
        limit=history_limit,
    )

    if conversation:

        conversation.customer_id = (
            customer.id
        )

        if matched_ticket is not None:
            conversation.ticket_id = (
                matched_ticket.id
            )

        db.add(
            conversation
        )

        db.commit()

    return {
        "available": True,

        "customer_id":
            customer.id,

        "customer_code":
            customer.customer_code,

        "customer":
            _model_to_dict(
                customer
            ),

        "current_order":
            (
                _model_to_dict(
                    matched_order
                )
                if matched_order
                else None
            ),

        "current_ticket":
            (
                _model_to_dict(
                    matched_ticket
                )
                if matched_ticket
                else None
            ),

        "orders": [
            _model_to_dict(order)
            for order in orders
        ],

        "returns": [
            _model_to_dict(
                return_request
            )
            for return_request
            in returns
        ],

        "tickets": [
            _model_to_dict(ticket)
            for ticket in tickets
        ],
    }