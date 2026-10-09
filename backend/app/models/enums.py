from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ShipmentStatus(str, Enum):
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELIVERY_FAILED = "delivery_failed"


class ReturnStatus(str, Enum):
    REQUESTED = "requested"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ITEM_RECEIVED = "item_received"
    REFUND_PROCESSED = "refund_processed"
    REPLACEMENT_SENT = "replacement_sent"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_APPROVAL = "waiting_approval"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class IssueType(str, Enum):
    DAMAGED_PRODUCT = "damaged_product"
    WRONG_PRODUCT = "wrong_product"
    RETURN_REQUEST = "return_request"
    REFUND_REQUEST = "refund_request"
    DELIVERY_ISSUE = "delivery_issue"
    PRODUCT_SUPPORT = "product_support"
    PAYMENT_ISSUE = "payment_issue"
    OTHER = "other"


class MessageSender(str, Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    HUMAN_AGENT = "human_agent"
    SYSTEM = "system"

class DocumentType(str, Enum):
    RETURNS_REFUNDS = "returns_refunds"
    DAMAGED_DEFECTIVE = "damaged_defective"
    SHIPPING_DELIVERY = "shipping_delivery"
    WARRANTY = "warranty"
    PAYMENT_REFUND = "payment_refund"
    PRODUCT_MANUAL = "product_manual"
    FAQ = "faq"
    OTHER = "other"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"