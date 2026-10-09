from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.action_execution import (
    ActionExecution,
)

from app.repositories.action_execution import (
    get_execution_by_approval_id,
)

from app.repositories.approval import (
    get_approval_by_code,
)

EXECUTABLE_ACTIONS = {
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
}


ACTION_REFERENCE_PREFIXES = {
    "create_replacement_request":
        "RPL",

    "issue_refund":
        "RFD",

    "issue_store_credit":
        "CRD",

    "cancel_order":
        "CAN",
}

def _simulate_business_action(
    action: str,
    order_number: str | None,
) -> tuple[str, str]:

    if action not in EXECUTABLE_ACTIONS:

        raise ValueError(
            "This action cannot be executed "
            "by ResolveIQ."
        )

    prefix = (
        ACTION_REFERENCE_PREFIXES[
            action
        ]
    )

    result_reference = (
        f"{prefix}-"
        f"{uuid4().hex[:8].upper()}"
    )

    if action == (
        "create_replacement_request"
    ):

        message = (
            "Replacement request was "
            "successfully created."
        )

    elif action == "issue_refund":

        message = (
            "Refund was successfully "
            "processed in the simulated "
            "ShopEase workflow."
        )

    elif action == "issue_store_credit":

        message = (
            "Store credit was successfully "
            "issued in the simulated "
            "ShopEase workflow."
        )

    else:

        message = (
            "Order cancellation was "
            "successfully processed in the "
            "simulated ShopEase workflow."
        )

    if order_number:

        message += (
            f" Order: {order_number}."
        )

    return (
        result_reference,
        message,
    )


def execute_approved_action(
    db: Session,
    approval_code: str,
) -> ActionExecution:

    approval = (
        get_approval_by_code(
            db=db,
            approval_code=(
                approval_code
            ),
        )
    )

    if approval is None:

        raise ValueError(
            "Approval request not found."
        )

    if approval.status != "approved":

        raise ValueError(
            "This action has not been "
            "approved for execution."
        )

    existing = (
        get_execution_by_approval_id(
            db=db,
            approval_request_id=(
                approval.id
            ),
        )
    )

    if existing is not None:

        return existing

    if (
        approval.action
        not in EXECUTABLE_ACTIONS
    ):

        raise ValueError(
            "The approved action is not "
            "supported by the executor."
        )

    execution = ActionExecution(
        execution_code=(
            "EXE-"
            + uuid4().hex[:8].upper()
        ),

        approval_request_id=(
            approval.id
        ),

        conversation_id=(
            approval.conversation_id
        ),

        order_number=(
            approval.order_number
        ),

        action=(
            approval.action
        ),

        status="processing",

        result_reference=None,

        result_message=None,

        error_message=None,

        executed_by=(
            "resolveiq_executor"
        ),

        created_at=(
            datetime.now(
                timezone.utc
            )
        ),

        executed_at=None,
    )

    db.add(
        execution
    )

    db.commit()

    db.refresh(
        execution
    )

    try:

        (
            result_reference,
            result_message,
        ) = _simulate_business_action(
            action=approval.action,

            order_number=(
                approval.order_number
            ),
        )

        execution.status = (
            "succeeded"
        )

        execution.result_reference = (
            result_reference
        )

        execution.result_message = (
            result_message
        )

        execution.executed_at = (
            datetime.now(
                timezone.utc
            )
        )

        db.commit()

        db.refresh(
            execution
        )

        return execution

    except Exception as exc:

        execution.status = "failed"

        execution.error_message = (
            str(exc)
        )

        execution.executed_at = (
            datetime.now(
                timezone.utc
            )
        )

        db.commit()

        db.refresh(
            execution
        )

        raise