import re

from functools import lru_cache
from pathlib import Path

from ollama import Client

from app.core.config import settings
from app.schemas.vision import (
    VisionAnalysisResult,
)

@lru_cache(maxsize=1)
def get_vision_client() -> Client:

    return Client(
        host=settings.ollama_base_url
    )

VALID_ISSUE_TYPES = {
    "damaged_product",
    "wrong_product",
    "package_damage",
    "screen_error",
    "other",
}


VALID_CONFIDENCE = {
    "high",
    "medium",
    "low",
}


VALID_EVIDENCE_QUALITY = {
    "sufficient",
    "partial",
    "poor",
}

def _extract_single_value(
    text: str,
    field: str,
) -> str | None:

    match = re.search(
        rf"(?im)^\s*"
        rf"{re.escape(field)}"
        rf"\s*:\s*(.+?)\s*$",
        text,
    )

    if not match:
        return None

    value = (
        match.group(1)
        .strip()
    )

    return value or None

def _extract_repeated_values(
    text: str,
    field: str,
) -> list[str]:

    matches = re.findall(
        rf"(?im)^\s*"
        rf"{re.escape(field)}"
        rf"\s*:\s*(.+?)\s*$",
        text,
    )

    return [
        value.strip()
        for value in matches
        if value.strip()
    ]

def _parse_vision_response(
    text: str,
) -> VisionAnalysisResult:

    issue_type = (
        _extract_single_value(
            text,
            "ISSUE_TYPE",
        )
        or "other"
    ).lower()

    confidence = (
        _extract_single_value(
            text,
            "CONFIDENCE",
        )
        or "low"
    ).lower()

    evidence_quality = (
        _extract_single_value(
            text,
            "EVIDENCE_QUALITY",
        )
        or "poor"
    ).lower()

    product_hint = (
        _extract_single_value(
            text,
            "PRODUCT_HINT",
        )
    )

    observations = (
        _extract_repeated_values(
            text,
            "OBSERVATION",
        )
    )

    visible_text = (
        _extract_repeated_values(
            text,
            "VISIBLE_TEXT",
        )
    )

    if (
        issue_type
        not in VALID_ISSUE_TYPES
    ):
        issue_type = "other"

    if (
        confidence
        not in VALID_CONFIDENCE
    ):
        confidence = "low"

    if (
        evidence_quality
        not in VALID_EVIDENCE_QUALITY
    ):
        evidence_quality = "poor"

    if not observations:

        observations = [
            (
                "No reliable visual "
                "observation was extracted."
            )
        ]

    return VisionAnalysisResult(
        issue_type=issue_type,
        confidence=confidence,
        observations=observations,
        visible_text=visible_text,
        product_hint=product_hint,
        evidence_quality=(
            evidence_quality
        ),
        raw_model_response=text,
    )

def analyze_support_image(
    image_path: Path,
    customer_question: str | None = None,
) -> VisionAnalysisResult:

    image_bytes = (
        image_path.read_bytes()
    )

    question = (
        customer_question.strip()
        if customer_question
        else (
            "Analyze the uploaded "
            "support image."
        )
    )

    client = (
        get_vision_client()
    )

    response = client.chat(
        model=settings.vision_model,
        messages=[
            {
                "role": "system",
                "content": """
You analyze customer-support images for
ShopEase.

Analyze ONLY what is visually observable.

Possible ISSUE_TYPE values:

damaged_product
wrong_product
package_damage
screen_error
other

Possible CONFIDENCE values:

high
medium
low

Possible EVIDENCE_QUALITY values:

sufficient
partial
poor

Rules:

- Do not decide refund eligibility.
- Do not decide replacement eligibility.
- Do not claim who caused damage.
- Do not invent product identity.
- PRODUCT_HINT is only a visual hint.
- Report visible physical damage precisely.
- Report visible text when readable.
- If the image is blurry, dark, obstructed,
  unrelated, or unclear, lower evidence quality.
- Do not assume an item matches an order.
  That will be verified separately.

Return exactly this format:

ISSUE_TYPE: <value>
CONFIDENCE: <value>
PRODUCT_HINT: <short hint or unknown>
EVIDENCE_QUALITY: <value>
OBSERVATION: <visual observation>
OBSERVATION: <another observation if needed>
VISIBLE_TEXT: <visible text if any>

You may use multiple OBSERVATION and
VISIBLE_TEXT lines.
"""
            },
            {
                "role": "user",
                "content": (
                    "Customer question:\n"
                    f"{question}"
                ),
                "images": [
                    image_bytes
                ],
            },
        ],
        options={
            "temperature": 0,
        },
    )

    raw_text = (
        response.message.content
        or ""    
    ).strip()

    if not raw_text:

        return VisionAnalysisResult(
            issue_type="other",
            confidence="low",
            observations=[
                (
                    "The vision model did "
                    "not return an analysis."
                )
            ],
            visible_text=[],
            product_hint=None,
            evidence_quality="poor",
            raw_model_response=None,
        )

    return _parse_vision_response(
        raw_text
    )