from functools import lru_cache
from typing import Literal

from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_ollama import (
    ChatOllama,
)
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
)
from ollama import Client

from app.core.config import settings

import re

SupportIntent = Literal[
    "damaged_product",
    "wrong_product",
    "return_request",
    "refund_request",
    "delivery_issue",
    "product_support",
    "payment_issue",
    "other",
]


class QueryRewriteResult(BaseModel):
    original_query: str
    rewritten_query: str
    intent: SupportIntent


INTENT_ALIASES: dict[str, SupportIntent] = {
    "damaged_product": "damaged_product",
    "damaged_item": "damaged_product",
    "damaged_item_replacement": "damaged_product",
    "damaged_product_replacement": "damaged_product",

    "wrong_product": "wrong_product",
    "wrong_item": "wrong_product",
    "incorrect_item": "wrong_product",

    "return_request": "return_request",
    "return": "return_request",

    "refund_request": "refund_request",
    "refund": "refund_request",

    "delivery_issue": "delivery_issue",
    "shipping_issue": "delivery_issue",
    "delivered_not_received": "delivery_issue",

    "product_support": "product_support",
    "product_issue": "product_support",
    "technical_support": "product_support",

    "payment_issue": "payment_issue",
    "payment": "payment_issue",

    "other": "other",
}


def normalize_intent(
    intent: str,
) -> SupportIntent:

    normalized = (
        intent.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return INTENT_ALIASES.get(
        normalized,
        "other",
    )


@lru_cache(maxsize=1)
def get_rewrite_client() -> Client:
    return Client(
        host=settings.ollama_base_url
    )

def _parse_rewrite_response(
    text: str,
) -> tuple[str, str]:

    text = text.strip()

    intent_match = re.search(
        r"(?im)^\s*"
        r"(?:intent|category)\s*:\s*"
        r"(.+?)\s*$",
        text,
    )

    query_match = re.search(
        r"(?im)^\s*"
        r"(?:query|rewritten_query)"
        r"\s*:\s*(.+?)\s*$",
        text,
    )

    if not intent_match:
        raise ValueError(
            "Query rewriter did not return "
            "an intent/category."
        )

    if not query_match:
        raise ValueError(
            "Query rewriter did not return "
            "a rewritten query."
        )

    intent = (
        intent_match
        .group(1)
        .strip()
    )

    rewritten_query = (
        query_match
        .group(1)
        .strip()
    )

    if not rewritten_query:
        raise ValueError(
            "Rewritten query was empty."
        )

    return (
        rewritten_query,
        intent,
    )

class QueryRewriteModelOutput(
    BaseModel
):
    rewritten_query: str = Field(
        validation_alias=AliasChoices(
            "rewritten_query",
            "query",
        ),
        description=(
            "Concise retrieval-focused "
            "customer support search query."
        ),
    )

    intent: str


class QueryRewriteResult(
    BaseModel
):
    original_query: str
    rewritten_query: str
    intent: SupportIntent


@lru_cache(maxsize=1)
def get_rewrite_model():

    model = ChatOllama(
        model=settings.reasoning_model,
        base_url=settings.ollama_base_url,
        temperature=0,
    )

    return model.with_structured_output(
        QueryRewriteModelOutput,
        method="json_schema",
    )

REWRITE_PROMPT = (
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You rewrite customer-support questions
into concise search queries for an
e-commerce knowledge retrieval system.

Rules:

1. Preserve the customer's actual intent.
2. Do not answer the question.
3. Do not invent order details, prices,
   dates, policy IDs, products, or facts
   that the customer did not provide.
4. Preserve important exact identifiers
   such as order numbers, policy IDs,
   model names, SKUs, prices, and dates.
5. Remove conversational filler.
6. Expand obvious support meaning when
   useful for retrieval.
7. Keep the rewritten query concise.
8. The intent must be one of the allowed
   support intent values.
9. Return only the structured fields
   requested by the schema.
10. Do not include explanations, labels,
    markdown, or additional prose.
The output fields must be:

rewritten_query
intent

The intent should preferably be exactly one of:

damaged_product
wrong_product
return_request
refund_request
delivery_issue
product_support
payment_issue
other
"""
            ),
            (
                "human",
                "Customer query:\n{query}",
            ),
        ]
    )
)

INTENT_ALIASES: dict[
    str,
    SupportIntent,
] = {
    "damaged_product":
        "damaged_product",

    "damaged_item":
        "damaged_product",

    "damaged_item_replacement":
        "damaged_product",

    "damaged_product_replacement":
        "damaged_product",

    "wrong_product":
        "wrong_product",

    "wrong_item":
        "wrong_product",

    "incorrect_item":
        "wrong_product",

    "return_request":
        "return_request",

    "return":
        "return_request",

    "refund_request":
        "refund_request",

    "refund":
        "refund_request",

    "delivery_issue":
        "delivery_issue",

    "shipping_issue":
        "delivery_issue",

    "delivered_not_received":
        "delivery_issue",

    "product_support":
        "product_support",

    "product_issue":
        "product_support",

    "technical_support":
        "product_support",

    "payment_issue":
        "payment_issue",

    "payment":
        "payment_issue",

    "other":
        "other",
}

def rewrite_query(
    query: str,
) -> QueryRewriteResult:

    query = query.strip()

    if not query:
        raise ValueError(
            "Query cannot be empty."
        )

    client = get_rewrite_client()

    response = client.chat(
        model=settings.reasoning_model,
        messages=[
            {
                "role": "system",
                "content": """
You rewrite customer-support questions
for an e-commerce knowledge retrieval system.

Do not answer the customer.

Do not invent facts.

Preserve useful identifiers such as
order IDs, policy IDs, SKUs, product
models, prices, and dates.

Remove conversational filler and create
a concise retrieval-focused query.

Choose the closest intent from:

damaged_product
wrong_product
return_request
refund_request
delivery_issue
product_support
payment_issue
other

Return exactly two lines:

INTENT: <intent>
QUERY: <rewritten query>

Do not add explanations or markdown.
""",
            },
            {
                "role": "user",
                "content": (
                    "Customer query:\n"
                    f"{query}"
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

    (
        rewritten_query,
        raw_intent,
    ) = _parse_rewrite_response(
        raw_text
    )

    return QueryRewriteResult(
        original_query=query,
        rewritten_query=(
            rewritten_query
        ),
        intent=normalize_intent(
            raw_intent
        ),
    )

    