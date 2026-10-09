from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.retrieval.advanced_retriever import (
    AdvancedRetriever,
)
from app.retrieval.citations import (
    build_citations,
)
from app.retrieval.evidence_assessor import (
    EvidenceAssessment,
    assess_evidence,
)
from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.retrieval.reranker import (
    rerank_results,
)
from app.retrieval.retry_query import (
    generate_retry_query,
)
from app.retrieval.types import (
    EvidenceCitation,
    RetrievalResult,
)

@dataclass
class GroundedRetrievalResult:
    original_query: str
    rewritten_query: str
    intent: str

    search_queries: list[str]

    applied_document_types: list[str]

    retrieval_attempts: int

    retry_query: str | None

    evidence_sufficient: bool

    assessment_reason: str

    missing_information: str | None

    results: list[
        RetrievalResult
    ]

    citations: list[
        EvidenceCitation
    ]

class GroundedRetriever:

    def __init__(self):
        self.advanced_retriever = (
            AdvancedRetriever()
        )

        self.hybrid_retriever = (
            HybridRetriever()
        )

    def retrieve(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
    ) -> GroundedRetrievalResult:

        advanced = (
            self.advanced_retriever
            .retrieve(
                db=db,
                query=query,
                top_k=top_k,
            )
        )

        final_results = (
            advanced.results
        )

        assessment = assess_evidence(
            query=query,
            results=final_results,
        )

        retrieval_attempts = 1

        retry_query = None

        if not assessment.sufficient:

            retry_query = (
                generate_retry_query(
                    original_query=query,

                    rewritten_query=(
                        advanced
                        .rewrite
                        .rewritten_query
                    ),

                    assessment=assessment,
                )
            )

            retrieval_attempts = 2

            retry_results = (
                self.hybrid_retriever
                .retrieve(
                    db=db,
                    query=retry_query,
                    top_k=max(
                        top_k * 2,
                        10,
                    ),
                    document_types=None,
                )
            )


            merged: dict[
                int,
                RetrievalResult,
            ] = {}

            for item in (
                final_results
                + retry_results
            ):
                if (
                    item.chunk_id
                    not in merged
                ):
                    merged[
                        item.chunk_id
                    ] = item

            merged_results = list(
                merged.values()
            )


            final_results = rerank_results(
                original_query=query,

                rewritten_query=(
                    retry_query
                ),

                candidates=(
                    merged_results
                ),

                top_k=top_k,
            )

            assessment = assess_evidence(
                query=query,
                results=final_results,
            )

        citations = build_citations(
            final_results
        )

        return GroundedRetrievalResult(
            original_query=query,

            rewritten_query=(
                advanced
                .rewrite
                .rewritten_query
            ),

            intent=(
                advanced.rewrite.intent
            ),

            search_queries=(
                advanced.search_queries
            ),

            applied_document_types=(
                advanced
                .applied_document_types
            ),

            retrieval_attempts=(
                retrieval_attempts
            ),

            retry_query=retry_query,

            evidence_sufficient=(
                assessment.sufficient
            ),

            assessment_reason=(
                assessment.reason
            ),

            missing_information=(
                assessment
                .missing_information
            ),

            results=final_results,

            citations=citations,
        )