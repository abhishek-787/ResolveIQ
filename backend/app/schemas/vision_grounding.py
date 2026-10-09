from pydantic import BaseModel

from app.schemas.vision import (
    VisionAnalysisResult,
)


class VisionGroundingResult(
    BaseModel,
):
    vision: VisionAnalysisResult

    order_number: str | None
    order_found: bool

    ordered_products: list[str]

    rag_query: str

    knowledge_success: bool
    evidence_sufficient: bool

    citations: list[dict]

