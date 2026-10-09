from pydantic import BaseModel

from app.db.session import SessionLocal
from app.retrieval.grounded_retriever import (
    GroundedRetriever,
)


class KnowledgeToolResult(BaseModel):
    tool_name: str = (
        "search_company_knowledge"
    )

    success: bool
    message: str

    evidence_sufficient: bool

    data: dict | None = None


grounded_retriever = (
    GroundedRetriever()
)

def search_company_knowledge(
    query: str,
    top_k: int = 5,
) -> KnowledgeToolResult:

    query = query.strip()

    if not query:
        return KnowledgeToolResult(
            success=False,
            message=(
                "Knowledge search query "
                "cannot be empty."
            ),
            evidence_sufficient=False,
        )

    try:

        with SessionLocal() as db:

            result = (
                grounded_retriever.retrieve(
                    db=db,
                    query=query,
                    top_k=top_k,
                )
            )

        citations = [
            {
                "citation_id":
                    citation.citation_id,

                "chunk_id":
                    citation.chunk_id,

                "document_code":
                    citation.document_code,

                "document_type":
                    citation.document_type,

                "version_label":
                    citation.version_label,

                "section_number":
                    citation.section_number,

                "section_title":
                    citation.section_title,

                "source_filename":
                    citation.source_filename,

                "content":
                    citation.content,

                "rank":
                    citation.rank,
            }

            for citation
            in result.citations
        ]

        return KnowledgeToolResult(
            success=True,

            message=(
                "ShopEase knowledge "
                "retrieval completed."
            ),

            evidence_sufficient=(
                result.evidence_sufficient
            ),

            data={
                "original_query":
                    result.original_query,

                "rewritten_query":
                    result.rewritten_query,

                "intent":
                    result.intent,

                "retrieval_attempts":
                    result.retrieval_attempts,

                "retry_query":
                    result.retry_query,

                "assessment_reason":
                    result.assessment_reason,

                "missing_information":
                    result.missing_information,

                "citations":
                    citations,
            },
        )

    except Exception as exc:

        return KnowledgeToolResult(
            success=False,

            message=(
                "Knowledge retrieval failed: "
                f"{exc}"
            ),

            evidence_sufficient=False,
        )

