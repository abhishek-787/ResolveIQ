import re
from functools import lru_cache

from ollama import Client

from app.core.config import settings


@lru_cache(maxsize=1)
def get_multi_query_client() -> Client:
    return Client(
        host=settings.ollama_base_url
    )


def _parse_alternative_queries(
    text: str,
) -> list[str]:

    text = text.strip()

    matches = re.findall(
        r"(?im)^\s*"
        r"(?:query|alt_query|alternative_query)"
        r"[_\s-]*\d+\s*:\s*(.+?)\s*$",
        text,
    )

    cleaned_queries = []

    seen = set()

    for query in matches:
        cleaned = query.strip()

        if not cleaned:
            continue

        key = cleaned.lower()

        if key in seen:
            continue

        seen.add(key)
        cleaned_queries.append(
            cleaned
        )

    return cleaned_queries[:2]


def generate_search_queries(
    rewritten_query: str,
    intent: str,
) -> list[str]:

    rewritten_query = (
        rewritten_query.strip()
    )

    if not rewritten_query:
        raise ValueError(
            "Rewritten query cannot be empty."
        )

    client = get_multi_query_client()

    response = client.chat(
        model=settings.reasoning_model,
        messages=[
            {
                "role": "system",
                "content": """
You generate alternative search queries
for an e-commerce customer-support
knowledge retrieval system.

The input query has already been rewritten.

Generate exactly TWO alternative search
queries that represent the SAME customer
problem from different useful retrieval
perspectives.

Rules:

1. Preserve the customer's intent.
2. Do not answer the question.
3. Do not invent facts.
4. Preserve exact identifiers such as
   policy IDs, order numbers, model names,
   SKUs, prices, and dates.
5. Keep each query concise.
6. The alternatives should emphasize
   different useful retrieval angles.

Return exactly:

QUERY_1: <first alternative query>
QUERY_2: <second alternative query>

Do not add explanations or markdown.
""",
            },
            {
                "role": "user",
                "content": (
                    f"Intent: {intent}\n"
                    f"Primary query: "
                    f"{rewritten_query}"
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

    alternatives = (
        _parse_alternative_queries(
            raw_text
        )
    )

    queries = [
        rewritten_query
    ]

    seen = {
        rewritten_query.lower()
    }

    for query in alternatives:

        key = query.lower()

        if key in seen:
            continue

        seen.add(key)
        queries.append(query)

    return queries[:3]