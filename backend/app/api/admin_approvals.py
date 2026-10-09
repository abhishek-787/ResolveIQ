from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.session import (
    get_db,
)

from app.repositories.approval import (
    list_pending_approvals,
)

from app.schemas.approval import (
    ApprovalRequestRead,
    ApprovalReviewRequest,
)

from app.services.approval_service import (
    approve_request,
    reject_request,
)

from app.repositories.approval import (
    get_approval_by_code,
    list_pending_approvals,
)

from app.schemas.execution import (
    ActionExecutionRead,
    ApproveAndExecuteResponse,
    AuditEvent,
)

from app.repositories.action_execution import (
    get_execution_by_approval_id,
)

from app.services.action_execution_service import (
    execute_approved_action,
)

router = APIRouter(
    prefix="/admin/approvals",
    tags=["Admin Approvals"],
)

@router.get(
    "",
    response_model=list[
        ApprovalRequestRead
    ],
)
def get_pending_approvals(
    db: Session = Depends(get_db),
):

    return list_pending_approvals(
        db=db
    )

@router.post(
    "/{approval_code}/approve",
    response_model=ApprovalRequestRead,
)
def approve_support_action(
    approval_code: str,
    payload: ApprovalReviewRequest,
    db: Session = Depends(get_db),
):

    try:

        return approve_request(
            db=db,

            approval_code=(
                approval_code
            ),

            reviewed_by=(
                payload.reviewed_by
            ),

            note=(
                payload.note
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{approval_code}/reject",
    response_model=ApprovalRequestRead,
)
def reject_support_action(
    approval_code: str,
    payload: ApprovalReviewRequest,
    db: Session = Depends(get_db),
):

    try:

        return reject_request(
            db=db,

            approval_code=(
                approval_code
            ),

            reviewed_by=(
                payload.reviewed_by
            ),

            note=(
                payload.note
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{approval_code}",
    response_model=ApprovalRequestRead,
)
def get_approval(
    approval_code: str,
    db: Session = Depends(get_db),
):

    approval = (
        get_approval_by_code(
            db=db,
            approval_code=approval_code,
        )
    )

    if approval is None:

        raise HTTPException(
            status_code=404,
            detail="Approval request not found.",
        )

    return approval


@router.post(
    "/{approval_code}/execute",
    response_model=ActionExecutionRead,
)
def execute_support_action(
    approval_code: str,
    db: Session = Depends(get_db),
):

    try:

        return execute_approved_action(
            db=db,
            approval_code=(
                approval_code
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{approval_code}/approve-and-execute",
    response_model=ApproveAndExecuteResponse,
)
def approve_and_execute_support_action(
    approval_code: str,
    payload: ApprovalReviewRequest,
    db: Session = Depends(get_db),
):

    approval = (
        get_approval_by_code(
            db=db,
            approval_code=(
                approval_code
            ),
        )
    )

    if approval is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Approval request not found."
            ),
        )

    if approval.status == "rejected":

        raise HTTPException(
            status_code=400,
            detail=(
                "Rejected approval requests "
                "cannot be executed."
            ),
        )

    try:

        if approval.status == "pending":

            approval = (
                approve_request(
                    db=db,

                    approval_code=(
                        approval_code
                    ),

                    reviewed_by=(
                        payload.reviewed_by
                    ),

                    note=(
                        payload.note
                    ),
                )
            )

        execution = (
            execute_approved_action(
                db=db,
                approval_code=(
                    approval_code
                ),
            )
        )

        return {
            "approval_code":
                approval.approval_code,

            "approval_status":
                approval.status,

            "execution":
                execution,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/{approval_code}/audit",
    response_model=list[
        AuditEvent
    ],
)
def get_approval_audit(
    approval_code: str,
    db: Session = Depends(get_db),
):

    approval = (
        get_approval_by_code(
            db=db,
            approval_code=(
                approval_code
            ),
        )
    )

    if approval is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Approval request not found."
            ),
        )

    events = [
        {
            "event_type":
                "approval_requested",

            "occurred_at":
                approval.requested_at,

            "actor":
                "resolveiq",

            "details":
                (
                    f"{approval.action} "
                    "was submitted for "
                    "human review."
                ),
        }
    ]

    if approval.reviewed_at:

        events.append(
            {
                "event_type":
                    (
                        "approval_"
                        f"{approval.status}"
                    ),

                "occurred_at":
                    approval.reviewed_at,

                "actor":
                    (
                        approval.reviewed_by
                        or "unknown"
                    ),

                "details":
                    (
                        approval.review_note
                        or (
                            "Human review "
                            "completed."
                        )
                    ),
            }
        )

    execution = (
        get_execution_by_approval_id(
            db=db,
            approval_request_id=(
                approval.id
            ),
        )
    )

    if execution:

        events.append(
            {
                "event_type":
                    "execution_started",

                "occurred_at":
                    execution.created_at,

                "actor":
                    execution.executed_by,

                "details":
                    (
                        f"Execution "
                        f"{execution.execution_code} "
                        "started."
                    ),
            }
        )

        if execution.executed_at:

            events.append(
                {
                    "event_type":
                        (
                            "execution_"
                            f"{execution.status}"
                        ),

                    "occurred_at":
                        execution.executed_at,

                    "actor":
                        execution.executed_by,

                    "details":
                        (
                            execution.result_message
                            or execution.error_message
                            or (
                                "Execution "
                                "completed."
                            )
                        ),
                }
            )

    events.sort(
        key=lambda event:
            event["occurred_at"]
    )

    return events