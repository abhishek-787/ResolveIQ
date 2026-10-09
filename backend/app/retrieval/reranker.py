import re
from dataclasses import replace
from functools import lru_cache

from ollama import Client

from app.core.config import settings
from app.retrieval.types import (
    RetrievalResult,
)


@lru_cache(maxsize=1)
def get_rerank_client() -> Client:
    return Client(
        host=settings.ollama_base_url
    )


def _parse_ranked_chunk_ids(
    text: str,
) -> list[int]:

    text = text.strip()

    match = re.search(
        r"(?im)^\s*"
        r"RANKED_CHUNK_IDS\s*:\s*"
        r"(.+?)\s*$",
        text,
    )

    if not match:
        return []

    id_text = match.group(1)

    ids = re.findall(
        r"\d+",
        id_text,
    )

    ranked_ids = []
    seen = set()

    for value in ids:

        chunk_id = int(value)

        if chunk_id in seen:
            continue

        seen.add(chunk_id)
        ranked_ids.append(
            chunk_id
        )

    return ranked_ids


def rerank_results(
    original_query: str,
    rewritten_query: str,
    candidates: list[
        RetrievalResult
    ],
    top_k: int = 5,
) -> list[RetrievalResult]:

    if not candidates:
        return []

    candidate_text = "\n\n".join(
        (
            f"CHUNK ID: {item.chunk_id}\n"
            f"DOCUMENT TYPE: "
            f"{item.document_type}\n"
            f"SECTION: "
            f"{item.section_title}\n"
            f"CONTENT:\n"
            f"{item.content[:1400]}"
        )
        for item in candidates
    )

    client = get_rerank_client()

    response = client.chat(
        model=settings.reasoning_model,
        messages=[
            {
                "role": "system",
                "content": """
You rerank retrieved ShopEase knowledge
chunks for a customer-support RAG system.

Rank chunks according to how directly
they support answering the customer's
question.

Prefer:

1. Direct policy evidence.
2. Specific eligibility rules.
3. Evidence requirements.
4. Relevant exceptions or limitations.
5. Resolution procedures.
6. Specific information over generic text.

Rules:

- Use ONLY the provided chunk IDs.
- Do not invent chunk IDs.
- Do not answer the customer.
- Do not explain your ranking.

Return exactly one line:

RANKED_CHUNK_IDS: <ids separated by commas>

Example:

RANKED_CHUNK_IDS: 12, 18, 7, 31
""",
            },
            {
                "role": "user",
                "content": (
                    "Original customer query:\n"
                    f"{original_query}\n\n"
                    "Rewritten retrieval query:\n"
                    f"{rewritten_query}\n\n"
                    "Candidate chunks:\n"
                    f"{candidate_text}"
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

    model_ids = (
        _parse_ranked_chunk_ids(
            raw_text
        )
    )

    by_id = {
        item.chunk_id: item
        for item in candidates
    }

    ordered_ids = []
    seen = set()

    # Accept only IDs that actually
    # exist in our retrieved candidates.
    for chunk_id in model_ids:

        if chunk_id not in by_id:
            continue

        if chunk_id in seen:
            continue

        ordered_ids.append(
            chunk_id
        )

        seen.add(chunk_id)

    # Safety fallback:
    # if Gemma omitted chunks or returned
    # unusable output, preserve retrieval
    # order instead of crashing.
    for item in candidates:

        if item.chunk_id in seen:
            continue

        ordered_ids.append(
            item.chunk_id
        )

        seen.add(
            item.chunk_id
        )

    reranked = []

    for rank, chunk_id in enumerate(
        ordered_ids[:top_k],
        start=1,
    ):

        item = by_id[
            chunk_id
        ]

        reranked.append(
            replace(
                item,
                retrieval_method=(
                    "advanced"
                ),
                rerank_rank=rank,
            )
        )

    return reranked