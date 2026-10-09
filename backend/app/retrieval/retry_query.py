import re
from functools import lru_cache

from ollama import Client

from app.core.config import settings
from app.retrieval.evidence_assessor import (
    EvidenceAssessment,
)


@lru_cache(maxsize=1)
def get_retry_client() -> Client:
    return Client(
        host=settings.ollama_base_url
    )

def generate_retry_query(
    original_query: str,
    rewritten_query: str,
    assessment: EvidenceAssessment,
) -> str:

    client = get_retry_client()

    missing = (
        assessment.missing_information
        or "additional relevant policy evidence"
    )

    response = client.chat(
        model=settings.reasoning_model,
        messages=[
            {
                "role": "system",
                "content": """
You create ONE improved retrieval query
when the first ShopEase knowledge search
did not find sufficient evidence.

Do not answer the customer.

Create a broader or more targeted search
query aimed specifically at finding the
missing policy information.

Preserve exact identifiers, model names,
prices, dates, order numbers, SKUs, and
policy IDs when present.

Do not invent facts.

Return exactly one line:

RETRY_QUERY: <query>
""",
            },
            {
                "role": "user",
                "content": (
                    "Original customer query:\n"
                    f"{original_query}\n\n"
                    "Previous retrieval query:\n"
                    f"{rewritten_query}\n\n"
                    "Missing evidence:\n"
                    f"{missing}"
                ),
            },
        ],
        options={
            "temperature": 0,
        },
    )

    raw_text = (
        response.message.content
        or ""
    )

    match = re.search(
        r"(?im)^\s*"
        r"RETRY_QUERY\s*:\s*"
        r"(.+?)\s*$",
        raw_text,
    )

    if match:
        retry_query = (
            match.group(1).strip()
        )

        if retry_query:
            return retry_query

    return (
        f"{rewritten_query} {missing}"
        .strip()
    )