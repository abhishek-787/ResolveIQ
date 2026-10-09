from app.models.enums import (
    DocumentType,
)


INTENT_DOCUMENT_TYPES = {

    "damaged_product": [
        DocumentType.DAMAGED_DEFECTIVE,
        DocumentType.RETURNS_REFUNDS,
        DocumentType.WARRANTY,
    ],

    "wrong_product": [
        DocumentType.RETURNS_REFUNDS,
        DocumentType.DAMAGED_DEFECTIVE,
    ],

    "return_request": [
        DocumentType.RETURNS_REFUNDS,
        DocumentType.WARRANTY,
    ],

    "refund_request": [
        DocumentType.RETURNS_REFUNDS,
        DocumentType.PAYMENT_REFUND,
        DocumentType.DAMAGED_DEFECTIVE,
    ],

    "delivery_issue": [
        DocumentType.SHIPPING_DELIVERY,
    ],

    "product_support": [
        DocumentType.PRODUCT_MANUAL,
        DocumentType.FAQ,
        DocumentType.WARRANTY,
    ],

    "payment_issue": [
        DocumentType.PAYMENT_REFUND,
        DocumentType.FAQ,
    ],
}

def document_types_for_intent(
        intent:str,
)-> list[DocumentType] | None:

    return INTENT_DOCUMENT_TYPES.get(
        intent
    )