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
    TicketResponse,
)
from app.services.support_lookup import (
    ResourceNotFoundError,
    find_ticket,
)


router = APIRouter(
    prefix="/tickets",
    tags=["Support Tickets"],
)


@router.get(
    "/{ticket_number}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_number: str,
    db: Session = Depends(get_db),
):
    try:
        return find_ticket(
            db,
            ticket_number,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc