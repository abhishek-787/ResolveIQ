from typing import Literal

from pydantic import BaseModel


VisionIssueType = Literal[
    "damaged_product",
    "wrong_product",
    "package_damage",
    "screen_error",
    "other",
]


VisionConfidence = Literal[
    "high",
    "medium",
    "low",
]


EvidenceQuality = Literal[
    "sufficient",
    "partial",
    "poor",
]


class VisionAnalysisResult(
    BaseModel,
):
    issue_type: VisionIssueType

    confidence: VisionConfidence

    observations: list[str]

    visible_text: list[str]

    product_hint: str | None = None

    evidence_quality: EvidenceQuality

    raw_model_response: str | None = None