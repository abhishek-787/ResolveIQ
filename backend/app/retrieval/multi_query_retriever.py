from dataclasses import (
    dataclass,
    replace,
)

from sqlalchemy.orm import Session

from app.models.enums import (
    DocumentType,
)
from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.retrieval.types import (
    RetrievalResult,
)


RRF_K = 60


@dataclass
class _MultiQueryCandidate:
    result: RetrievalResult
    fusion_score: float = 0.0
    query_hits: int = 0


class MultiQueryRetriever:

    def __init__(self):
        self.hybrid_retriever = (
            HybridRetriever()
        )

    def retrieve(
        self,
        db: Session,
        queries: list[str],
        top_k: int = 12,
        document_types: list[
            DocumentType
        ] | None = None,
    ) -> list[RetrievalResult]:

        candidates: dict[
            int,
            _MultiQueryCandidate,
        ] = {}

        for query in queries:

            results = (
                self.hybrid_retriever
                .retrieve(
                    db=db,
                    query=query,
                    top_k=top_k,
                    document_types=(
                        document_types
                    ),
                )
            )

            for rank, result in enumerate(
                results,
                start=1,
            ):

                candidate = candidates.get(
                    result.chunk_id
                )

                if candidate is None:
                    candidate = (
                        _MultiQueryCandidate(
                            result=result
                        )
                    )

                    candidates[
                        result.chunk_id
                    ] = candidate

                candidate.fusion_score += (
                    1.0
                    / (
                        RRF_K
                        + rank
                    )
                )

                candidate.query_hits += 1

        ranked = sorted(
            candidates.values(),
            key=lambda candidate:
                candidate.fusion_score,
            reverse=True,
        )

        final_results = []

        for candidate in ranked[
            :top_k
        ]:

            final_results.append(
                replace(
                    candidate.result,

                    score=round(
                        candidate.fusion_score,
                        6,
                    ),

                    retrieval_method=(
                        "multi_query_hybrid"
                    ),

                    vector_rank=None,
                    bm25_rank=None,

                    vector_score=None,
                    bm25_score=None,

                    query_hits=(
                        candidate.query_hits
                    ),
                )
            )

        return final_results