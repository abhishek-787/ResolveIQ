from pathlib import Path

from app.agent.tools.business_tools import (
    get_order,
)

from app.agent.tools.knowledge_tools import (
    search_company_knowledge,
)

from app.schemas.vision import (
    VisionAnalysisResult,
)

from app.schemas.vision_grounding import (
    VisionGroundingResult,
)

from app.services.vision_analysis import (
    analyze_support_image,
)

def _mock_damaged_monitor_vision(
) -> VisionAnalysisResult:

    return VisionAnalysisResult(
        issue_type="damaged_product",

        confidence="high",

        observations=[
            (
                "A visible crack runs "
                "across the display panel."
            ),
        ],

        visible_text=[
            "AeroView"
        ],

        product_hint=(
            "computer monitor"
        ),

        evidence_quality=(
            "sufficient"
        ),

        raw_model_response=(
            "MOCK_VISION_RESULT"
        ),
    )

def _get_product_names(
    order_data: dict | None,
) -> list[str]:

    if not order_data:
        return []

    items = (
        order_data.get(
            "items"
        )
        or []
    )

    names = []

    for item in items:

        product = (
            item.get(
                "product"
            )
            or {}
        )

        name = (
            product.get("name")
            or product.get(
                "product_name"
            )
            or product.get(
                "title"
            )
        )

        if name:
            names.append(
                str(name)
            )

    return names

def _build_rag_query(
    question: str,
    vision: VisionAnalysisResult,
    order_number: str | None,
    product_names: list[str],
) -> str:

    parts = [
        (
            "Customer question: "
            f"{question}"
        ),

        (
            "Visual issue: "
            f"{vision.issue_type}."
        ),
    ]

    if vision.observations:

        parts.append(
            (
                "Visible observations: "
                + " ".join(
                    vision.observations
                )
            )
        )

    if order_number:

        parts.append(
            (
                "ShopEase order: "
                f"{order_number}."
            )
        )

    if product_names:

        parts.append(
            (
                "Verified ordered product: "
                f"{', '.join(product_names)}."
            )
        )

    if vision.product_hint:

        parts.append(
            (
                "Visual product hint: "
                f"{vision.product_hint}."
            )
        )

    parts.append(
        (
            "Find the relevant ShopEase "
            "policy, evidence requirements, "
            "and available resolution rules."
        )
    )

    return "\n".join(
        parts
    )

def ground_vision_case(
    image_path: Path,
    question: str,
    order_number: str | None = None,
    use_mock_vision: bool = False,
) -> VisionGroundingResult:

    # 1. Vision
    if use_mock_vision:

        vision = (
            _mock_damaged_monitor_vision()
        )

    else:

        vision = (
            analyze_support_image(
                image_path=image_path,
                customer_question=(
                    question
                ),
            )
        )

    # 2. Order
    normalized_order = None
    order_found = False
    order_data = None

    if order_number:

        normalized_order = (
            order_number
            .strip()
            .upper()
        )

        order_result = (
            get_order(
                normalized_order
            )
        )

        order_found = (
            order_result.success
        )

        if order_result.success:
            order_data = (
                order_result.data
            )

    # 3. Products
    product_names = (
        _get_product_names(
            order_data
        )
    )

    # 4. Build RAG query
    rag_query = (
        _build_rag_query(
            question=question,
            vision=vision,
            order_number=(
                normalized_order
            ),
            product_names=(
                product_names
            ),
        )
    )

    # 5. Existing Phase 3 RAG
    knowledge = (
        search_company_knowledge(
            rag_query
        )
    )

    knowledge_data = (
        knowledge.data
        or {}
    )

    return VisionGroundingResult(
        vision=vision,

        order_number=(
            normalized_order
        ),

        order_found=(
            order_found
        ),

        ordered_products=(
            product_names
        ),

        rag_query=(
            rag_query
        ),

        knowledge_success=(
            knowledge.success
        ),

        evidence_sufficient=(
            knowledge
            .evidence_sufficient
        ),

        citations=(
            knowledge_data.get(
                "citations"
            )
            or []
        ),
    )