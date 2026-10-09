from datetime import (
    datetime,
    timezone,
)
from decimal import Decimal

from sqlalchemy import (
    select,
)

from app.db.session import (
    SessionLocal,
)
from app.models import (
    Conversation,
    Customer,
    Message,
    Order,
    OrderItem,
    Product,
    ReturnRequest,
    Shipment,
    SupportTicket,
)
from app.models.enums import (
    IssueType,
    MessageSender,
    OrderStatus,
    PaymentStatus,
    ReturnStatus,
    ShipmentStatus,
    TicketPriority,
    TicketStatus,
)


def dt(
    year: int,
    month: int,
    day: int,
    hour: int = 10,
) -> datetime:
    return datetime(
        year,
        month,
        day,
        hour,
        tzinfo=timezone.utc,
    )


def seed_database() -> None:
    with SessionLocal() as session:

        existing_customer = session.scalar(
            select(Customer.id).limit(1)
        )

        if existing_customer is not None:
            print(
                "ShopEase seed data already exists. "
                "Skipping."
            )
            return

        # -------------------------------------------------
        # PRODUCTS
        # -------------------------------------------------

        monitor = Product(
            sku="SE-MON-AV27Q",
            name='AeroView 27" QHD Monitor',
            category="Electronics",
            brand="AeroView",
            description=(
                "27-inch QHD IPS monitor with "
                "165 Hz refresh rate, HDMI and "
                "DisplayPort connectivity."
            ),
            price=Decimal("21999.00"),
        )

        headphones = Product(
            sku="SE-AUD-SPX500",
            name="SonicPulse X500 Wireless Headphones",
            category="Electronics",
            brand="SonicPulse",
            description=(
                "Wireless over-ear headphones with "
                "active noise cancellation and "
                "USB-C charging."
            ),
            price=Decimal("8999.00"),
        )

        smartwatch = Product(
            sku="SE-WEAR-FC2",
            name="FitCore Active 2 Smartwatch",
            category="Wearables",
            brand="FitCore",
            description=(
                "Fitness smartwatch with heart-rate "
                "tracking, GPS and activity monitoring."
            ),
            price=Decimal("7499.00"),
        )

        coffee_maker = Product(
            sku="SE-HOME-HB12",
            name="HomeBrew 12-Cup Coffee Maker",
            category="Home Appliances",
            brand="HomeBrew",
            description=(
                "Programmable drip coffee maker "
                "with 12-cup glass carafe."
            ),
            price=Decimal("4299.00"),
        )

        keyboard = Product(
            sku="SE-PC-NK87",
            name="NovaKey K87 Mechanical Keyboard",
            category="Computer Accessories",
            brand="NovaKey",
            description=(
                "Tenkeyless mechanical keyboard "
                "with hot-swappable switches and "
                "RGB lighting."
            ),
            price=Decimal("5499.00"),
        )

        session.add_all(
            [
                monitor,
                headphones,
                smartwatch,
                coffee_maker,
                keyboard,
            ]
        )

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------

        rahul = Customer(
            customer_code="CUST-1001",
            full_name="Rahul Sharma",
            email="rahul.sharma@example.com",
            phone="+91-9000001001",
            address=(
                "Indiranagar, Bengaluru, "
                "Karnataka, India"
            ),
        )

        ananya = Customer(
            customer_code="CUST-1002",
            full_name="Ananya Rao",
            email="ananya.rao@example.com",
            phone="+91-9000001002",
            address=(
                "Madhapur, Hyderabad, "
                "Telangana, India"
            ),
        )

        arjun = Customer(
            customer_code="CUST-1003",
            full_name="Arjun Mehta",
            email="arjun.mehta@example.com",
            phone="+91-9000001003",
            address=(
                "Andheri East, Mumbai, "
                "Maharashtra, India"
            ),
        )

        priya = Customer(
            customer_code="CUST-1004",
            full_name="Priya Nair",
            email="priya.nair@example.com",
            phone="+91-9000001004",
            address=(
                "T Nagar, Chennai, "
                "Tamil Nadu, India"
            ),
        )

        karan = Customer(
            customer_code="CUST-1005",
            full_name="Karan Singh",
            email="karan.singh@example.com",
            phone="+91-9000001005",
            address=(
                "Sector 62, Noida, "
                "Uttar Pradesh, India"
            ),
        )

        session.add_all(
            [
                rahul,
                ananya,
                arjun,
                priya,
                karan,
            ]
        )

        session.flush()

        # -------------------------------------------------
        # ORDERS
        # -------------------------------------------------

        order_monitor = Order(
            order_number="ORD-10482",
            customer=rahul,
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount=Decimal("21999.00"),
            shipping_address=rahul.address,
            ordered_at=dt(2026, 9, 25),
        )

        order_headphones = Order(
            order_number="ORD-10483",
            customer=ananya,
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount=Decimal("8999.00"),
            shipping_address=ananya.address,
            ordered_at=dt(2026, 9, 20),
        )

        order_watch = Order(
            order_number="ORD-10484",
            customer=arjun,
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount=Decimal("7499.00"),
            shipping_address=arjun.address,
            ordered_at=dt(2026, 9, 10),
        )

        order_coffee = Order(
            order_number="ORD-10485",
            customer=priya,
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount=Decimal("4299.00"),
            shipping_address=priya.address,
            ordered_at=dt(2026, 9, 24),
        )

        order_keyboard = Order(
            order_number="ORD-10486",
            customer=karan,
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount=Decimal("5499.00"),
            shipping_address=karan.address,
            ordered_at=dt(2026, 9, 18),
        )

        session.add_all(
            [
                order_monitor,
                order_headphones,
                order_watch,
                order_coffee,
                order_keyboard,
            ]
        )

        session.flush()

        # -------------------------------------------------
        # ORDER ITEMS
        # -------------------------------------------------

        session.add_all(
            [
                OrderItem(
                    order=order_monitor,
                    product=monitor,
                    quantity=1,
                    unit_price=Decimal(
                        "21999.00"
                    ),
                ),
                OrderItem(
                    order=order_headphones,
                    product=headphones,
                    quantity=1,
                    unit_price=Decimal(
                        "8999.00"
                    ),
                ),
                OrderItem(
                    order=order_watch,
                    product=smartwatch,
                    quantity=1,
                    unit_price=Decimal(
                        "7499.00"
                    ),
                ),
                OrderItem(
                    order=order_coffee,
                    product=coffee_maker,
                    quantity=1,
                    unit_price=Decimal(
                        "4299.00"
                    ),
                ),
                OrderItem(
                    order=order_keyboard,
                    product=keyboard,
                    quantity=1,
                    unit_price=Decimal(
                        "5499.00"
                    ),
                ),
            ]
        )

        # -------------------------------------------------
        # SHIPMENTS
        # -------------------------------------------------

        session.add_all(
            [
                Shipment(
                    order=order_monitor,
                    tracking_number="TRK-SE-88001",
                    carrier="SwiftShip",
                    status=ShipmentStatus.DELIVERED,
                    shipped_at=dt(
                        2026, 9, 26
                    ),
                    delivered_at=dt(
                        2026, 9, 29
                    ),
                    estimated_delivery=dt(
                        2026, 9, 29
                    ),
                ),
                Shipment(
                    order=order_headphones,
                    tracking_number="TRK-SE-88002",
                    carrier="ParcelJet",
                    status=ShipmentStatus.DELIVERED,
                    shipped_at=dt(
                        2026, 9, 21
                    ),
                    delivered_at=dt(
                        2026, 9, 24
                    ),
                    estimated_delivery=dt(
                        2026, 9, 24
                    ),
                ),
                Shipment(
                    order=order_watch,
                    tracking_number="TRK-SE-88003",
                    carrier="SwiftShip",
                    status=ShipmentStatus.DELIVERED,
                    shipped_at=dt(
                        2026, 9, 11
                    ),
                    delivered_at=dt(
                        2026, 9, 14
                    ),
                    estimated_delivery=dt(
                        2026, 9, 14
                    ),
                ),
                Shipment(
                    order=order_coffee,
                    tracking_number="TRK-SE-88004",
                    carrier="QuickRoute",
                    status=ShipmentStatus.DELIVERED,
                    shipped_at=dt(
                        2026, 9, 25
                    ),
                    delivered_at=dt(
                        2026, 9, 28
                    ),
                    estimated_delivery=dt(
                        2026, 9, 28
                    ),
                ),
                Shipment(
                    order=order_keyboard,
                    tracking_number="TRK-SE-88005",
                    carrier="ParcelJet",
                    status=ShipmentStatus.DELIVERED,
                    shipped_at=dt(
                        2026, 9, 19
                    ),
                    delivered_at=dt(
                        2026, 9, 22
                    ),
                    estimated_delivery=dt(
                        2026, 9, 22
                    ),
                ),
            ]
        )

        # -------------------------------------------------
        # RETURN REQUEST
        # -------------------------------------------------

        session.add(
            ReturnRequest(
                return_number="RET-3001",
                order=order_watch,
                reason="Battery performance issue",
                details=(
                    "Customer reports battery life "
                    "of approximately four hours "
                    "under normal daily use."
                ),
                status=ReturnStatus.UNDER_REVIEW,
                requested_at=dt(
                    2026, 9, 29
                ),
            )
        )

        # -------------------------------------------------
        # SUPPORT TICKETS
        # -------------------------------------------------

        damaged_ticket = SupportTicket(
            ticket_number="TKT-2001",
            customer=rahul,
            order=order_monitor,
            issue_type=(
                IssueType.DAMAGED_PRODUCT
            ),
            subject=(
                "Monitor arrived with "
                "cracked screen"
            ),
            description=(
                "The monitor was delivered today. "
                "After opening the package, the "
                "customer found a visible crack "
                "across the display."
            ),
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
        )

        wrong_item_ticket = SupportTicket(
            ticket_number="TKT-2002",
            customer=ananya,
            order=order_headphones,
            issue_type=(
                IssueType.WRONG_PRODUCT
            ),
            subject="Incorrect item received",
            description=(
                "Customer ordered SonicPulse X500 "
                "headphones but reports receiving "
                "a different headphone model."
            ),
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
        )

        return_ticket = SupportTicket(
            ticket_number="TKT-2003",
            customer=arjun,
            order=order_watch,
            issue_type=(
                IssueType.RETURN_REQUEST
            ),
            subject=(
                "Smartwatch battery drains "
                "within four hours"
            ),
            description=(
                "Customer reports significantly "
                "shorter battery life than expected "
                "and has requested a return."
            ),
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.IN_PROGRESS,
        )

        delivery_ticket = SupportTicket(
            ticket_number="TKT-2004",
            customer=priya,
            order=order_coffee,
            issue_type=(
                IssueType.DELIVERY_ISSUE
            ),
            subject=(
                "Package marked delivered "
                "but not received"
            ),
            description=(
                "Carrier tracking shows delivered, "
                "but the customer states that the "
                "parcel was not received."
            ),
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
        )

        support_ticket = SupportTicket(
            ticket_number="TKT-2005",
            customer=karan,
            order=order_keyboard,
            issue_type=(
                IssueType.PRODUCT_SUPPORT
            ),
            subject=(
                "Keyboard not detected "
                "after connection"
            ),
            description=(
                "Customer connected the NovaKey K87 "
                "using USB but Windows does not "
                "detect the keyboard."
            ),
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
        )

        session.add_all(
            [
                damaged_ticket,
                wrong_item_ticket,
                return_ticket,
                delivery_ticket,
                support_ticket,
            ]
        )

        session.flush()

        # -------------------------------------------------
        # CONVERSATIONS + INITIAL CUSTOMER MESSAGES
        # -------------------------------------------------

        conversation_data = [
            (
                rahul,
                damaged_ticket,
                (
                    "My monitor arrived today and "
                    "the screen is cracked. "
                    "Can I get a replacement?"
                ),
            ),
            (
                ananya,
                wrong_item_ticket,
                (
                    "I ordered SonicPulse X500 "
                    "headphones but the model inside "
                    "the box is different."
                ),
            ),
            (
                arjun,
                return_ticket,
                (
                    "The smartwatch battery lasts "
                    "only around four hours. "
                    "I would like to return it."
                ),
            ),
            (
                priya,
                delivery_ticket,
                (
                    "Tracking says my coffee maker "
                    "was delivered, but I haven't "
                    "received the package."
                ),
            ),
            (
                karan,
                support_ticket,
                (
                    "My NovaKey keyboard powers on "
                    "but my computer is not "
                    "detecting it."
                ),
            ),
        ]

        for (
            customer,
            ticket,
            message_text,
        ) in conversation_data:

            conversation = Conversation(
                customer=customer,
                ticket=ticket,
            )

            conversation.messages.append(
                Message(
                    sender=(
                        MessageSender.CUSTOMER
                    ),
                    content=message_text,
                )
            )

            session.add(
                conversation
            )

        session.commit()

        print(
            "ShopEase synthetic ecommerce "
            "data seeded successfully."
        )


if __name__ == "__main__":
    seed_database()