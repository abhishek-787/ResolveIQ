from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.db.session import (
    get_db,
)

from app.repositories.agent_run_log import (
    get_agent_run_by_code,
    list_recent_agent_runs,
)

from app.schemas.observability import (
    AgentRunLogRead,
)


router = APIRouter(
    prefix="/admin/observability",
    tags=["Admin Observability"],
)

@router.get(
    "/runs",
    response_model=list[
        AgentRunLogRead
    ],
)
def get_recent_runs(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    db: Session = Depends(
        get_db
    ),
):

    return list_recent_agent_runs(
        db=db,
        limit=limit,
    )

@router.get(
    "/runs/{run_code}",
    response_model=AgentRunLogRead,
)
def get_run(
    run_code: str,
    db: Session = Depends(
        get_db
    ),
):

    run = (
        get_agent_run_by_code(
            db=db,
            run_code=run_code,
        )
    )

    if run is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Agent run not found."
            ),
        )

    return run