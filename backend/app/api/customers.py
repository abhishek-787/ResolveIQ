from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import (
    Session,
)

from app.db.session import (
    get_db,
)
from app.schemas.business import (
    CustomerResponse,
    OrderSummary,
)
from app.services.support_lookup import (
    ResourceNotFoundError,
    find_customer,
    find_customer_orders,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.get(
    "/{customer_code}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_code: str,
    db: Session = Depends(get_db),
):
    try:
        return find_customer(
            db,
            customer_code,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{customer_code}/orders",
    response_model=list[OrderSummary],
)
def get_customer_order_history(
    customer_code: str,
    db: Session = Depends(get_db),
):
    try:
        return find_customer_orders(
            db,
            customer_code,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc