from typing import Literal

from pydantic import BaseModel


ResolutionAction = Literal[
    "provide_information",
    "request_more_information",
    "create_return_request",
    "create_replacement_request",
    "issue_refund",
    "issue_store_credit",
    "cancel_order",
    "escalate_to_human",
]


ResolutionConfidence = Literal[
    "high",
    "medium",
    "low",
]


class ResolutionProposal(
    BaseModel,
):
    action: ResolutionAction

    confidence: ResolutionConfidence

    reason: str

    missing_information: str | None = None