from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.models.enums import (
    IssueType,
    OrderStatus,
    PaymentStatus,
    ReturnStatus,
    ShipmentStatus,
    TicketPriority,
    TicketStatus,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerResponse(ORMModel):
    customer_code: str
    full_name: str
    email: str
    phone: str | None
    address: str | None


class ProductBrief(ORMModel):
    sku: str
    name: str
    category: str
    brand: str


class OrderItemResponse(ORMModel):
    quantity: int
    unit_price: Decimal
    product: ProductBrief


class ShipmentResponse(ORMModel):
    tracking_number: str
    carrier: str
    status: ShipmentStatus
    shipped_at: datetime | None
    delivered_at: datetime | None
    estimated_delivery: datetime | None


class ReturnResponse(ORMModel):
    return_number: str
    reason: str
    details: str | None
    status: ReturnStatus
    requested_at: datetime
    resolved_at: datetime | None


class OrderSummary(ORMModel):
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: Decimal
    ordered_at: datetime


class OrderDetail(OrderSummary):
    shipping_address: str

    customer: CustomerResponse

    items: list[
        OrderItemResponse
    ]

    shipments: list[
        ShipmentResponse
    ]

    return_requests: list[
        ReturnResponse
    ]


class TicketResponse(ORMModel):
    ticket_number: str

    issue_type: IssueType

    subject: str
    description: str

    priority: TicketPriority
    status: TicketStatus

    resolution_summary: str | None

    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    customer: CustomerResponse

    order: OrderSummary | None