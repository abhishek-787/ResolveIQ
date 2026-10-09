from typing import Literal

from pydantic import BaseModel

from app.schemas.resolution import (
    ResolutionAction,
)


GuardrailStatus = Literal[
    "allowed",
    "needs_information",
    "needs_human_approval",
    "blocked",
]


class GuardrailDecision(
    BaseModel,
):
    action: ResolutionAction

    status: GuardrailStatus

    can_execute_now: bool

    requires_human_approval: bool

    reason: str

    violations: list[str]