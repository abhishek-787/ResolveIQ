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
    OrderDetail,
    ShipmentResponse,
)
from app.services.support_lookup import (
    ResourceNotFoundError,
    find_order,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get(
    "/{order_number}",
    response_model=OrderDetail,
)
def get_order(
    order_number: str,
    db: Session = Depends(get_db),
):
    try:
        return find_order(
            db,
            order_number,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{order_number}/shipments",
    response_model=list[
        ShipmentResponse
    ],
)
def get_order_shipments(
    order_number: str,
    db: Session = Depends(get_db),
):
    try:
        order = find_order(
            db,
            order_number,
        )

        return order.shipments

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc