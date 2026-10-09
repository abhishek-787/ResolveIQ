import re
from functools import lru_cache

from ollama import Client
from pydantic import BaseModel

from app.core.config import settings
from app.retrieval.types import (
    RetrievalResult,
)


class EvidenceAssessment(BaseModel):
    sufficient: bool
    reason: str
    missing_information: str | None = None


@lru_cache(maxsize=1)
def get_evidence_client() -> Client:
    return Client(
        host=settings.ollama_base_url
    )

def _parse_assessment(
    text: str,
) -> EvidenceAssessment:

    text = text.strip()

    sufficient_match = re.search(
        r"(?im)^\s*"
        r"SUFFICIENT\s*:\s*"
        r"(yes|no)\s*$",
        text,
    )

    reason_match = re.search(
        r"(?im)^\s*"
        r"REASON\s*:\s*(.+?)\s*$",
        text,
    )

    missing_match = re.search(
        r"(?im)^\s*"
        r"MISSING\s*:\s*(.+?)\s*$",
        text,
    )

    if not sufficient_match:
        return EvidenceAssessment(
            sufficient=False,
            reason=(
                "Evidence assessment "
                "could not be parsed."
            ),
            missing_information=(
                "Unknown"
            ),
        )

    sufficient = (
        sufficient_match
        .group(1)
        .lower()
        == "yes"
    )

    reason = (
        reason_match.group(1).strip()
        if reason_match
        else "No reason provided."
    )

    missing = (
        missing_match.group(1).strip()
        if missing_match
        else None
    )

    if missing and (
        missing.lower()
        in {
            "none",
            "nothing",
            "n/a",
        }
    ):
        missing = None

    return EvidenceAssessment(
        sufficient=sufficient,
        reason=reason,
        missing_information=missing,
    )

def assess_evidence(
    query: str,
    results: list[RetrievalResult],
) -> EvidenceAssessment:

    if not results:
        return EvidenceAssessment(
            sufficient=False,
            reason=(
                "No relevant evidence "
                "was retrieved."
            ),
            missing_information=(
                "Relevant ShopEase policy "
                "or support documentation."
            ),
        )

    evidence_text = "\n\n".join(
        (
            f"CHUNK ID: {item.chunk_id}\n"
            f"DOCUMENT: "
            f"{item.document_type}\n"
            f"SECTION: "
            f"{item.section_title}\n"
            f"CONTENT:\n"
            f"{item.content[:1600]}"
        )
        for item in results
    )

    client = get_evidence_client()

    response = client.chat(
        model=settings.reasoning_model,
        messages=[
            {
                "role": "system",
                "content": """
You evaluate whether retrieved ShopEase
knowledge contains enough evidence to
answer a customer-support question.

Do NOT answer the customer.

Judge only from the supplied evidence.

Evidence is sufficient only when the
chunks collectively contain the important
policy, eligibility, evidence, limitation,
or procedure information needed for the
customer's question.

Do not assume missing ShopEase policy
rules from general knowledge.

If important information is missing,
mark the evidence insufficient.

Return exactly three lines:

SUFFICIENT: yes or no
REASON: <short reason>
MISSING: <missing evidence or none>

Do not add markdown or explanations.
""",
            },
            {
                "role": "user",
                "content": (
                    "Customer question:\n"
                    f"{query}\n\n"
                    "Retrieved evidence:\n"
                    f"{evidence_text}"
                ),
            },
        ],
        options={
            "temperature": 0,
        },
    )

    return _parse_assessment(
        response.message.content
        or ""
    )

def assess_evidence(
    query: str,
    results: list[RetrievalResult],
) -> EvidenceAssessment:

    if not results:
        return EvidenceAssessment(
            sufficient=False,
            reason=(
                "No relevant evidence "
                "was retrieved."
            ),
            missing_information=(
                "Relevant ShopEase policy "
                "or support documentation."
            ),
        )

    evidence_text = "\n\n".join(
        (
            f"CHUNK ID: {item.chunk_id}\n"
            f"DOCUMENT: "
            f"{item.document_type}\n"
            f"SECTION: "
            f"{item.section_title}\n"
            f"CONTENT:\n"
            f"{item.content[:1600]}"
        )
        for item in results
    )

    client = get_evidence_client()

    response = client.chat(
        model=settings.reasoning_model,
        messages=[
            {
                "role": "system",
                "content": """
You evaluate whether retrieved ShopEase
knowledge contains enough evidence to
answer a customer-support question.

Do NOT answer the customer.

Judge only from the supplied evidence.

Evidence is sufficient only when the
chunks collectively contain the important
policy, eligibility, evidence, limitation,
or procedure information needed for the
customer's question.

Do not assume missing ShopEase policy
rules from general knowledge.

If important information is missing,
mark the evidence insufficient.

Return exactly three lines:

SUFFICIENT: yes or no
REASON: <short reason>
MISSING: <missing evidence or none>

Do not add markdown or explanations.
""",
            },
            {
                "role": "user",
                "content": (
                    "Customer question:\n"
                    f"{query}\n\n"
                    "Retrieved evidence:\n"
                    f"{evidence_text}"
                ),
            },
        ],
        options={
            "temperature": 0,
        },
    )

    return _parse_assessment(
        response.message.content
        or ""
    )