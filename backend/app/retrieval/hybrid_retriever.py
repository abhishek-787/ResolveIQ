from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.retrieval.bm25_retriever import (
    BM25Retriever,
)
from app.retrieval.types import (
    RetrievalResult,
)
from app.retrieval.vector_retriever import (
    VectorRetriever,
)
from app.models.enums import (
    DocumentType,
)


RRF_K = 60

@dataclass
class _FusionCandidate:
    result: RetrievalResult

    vector_rank: int | None = None
    bm25_rank: int | None = None

    vector_score: float | None = None
    bm25_score: float | None = None

    rrf_score: float = 0.0

class HybridRetriever:

    def __init__(self,default_top_k: int = 8,candidate_multiplier: int = 2,):

        self.default_top_k = (
            default_top_k
        )

        self.candidate_multiplier = (
            candidate_multiplier
        )

        self.vector_retriever = (
            VectorRetriever()
        )

        self.bm25_retriever = (
            BM25Retriever()
        )

    def retrieve(
            self,
            db: Session,
            query: str,
            top_k: int | None = None,
            document_types: list[DocumentType] | None = None,) -> list[RetrievalResult]:

        query = query.strip()

        if not query:
            return []

        final_top_k = (
            top_k
            if top_k is not None
            else self.default_top_k
        )

        candidate_k = max(
            final_top_k
            * self.candidate_multiplier,
            final_top_k,
        )

        vector_results = (self.vector_retriever.retrieve(
            db=db,
            top_k=candidate_k,
            query=query,
            document_types = document_types,
        )
        )

        bm25_results = (
            self.bm25_retriever.retrieve(
                db=db,
                query=query,
                top_k=candidate_k,
                document_types= document_types,
            )
        )

        candidates: dict[
            int,
            _FusionCandidate,
        ] = {}

        for rank,result in enumerate(
            vector_results,
            start=1,
        ):
            candidate = candidates.get(
                result.chunk_id
            )

            if candidate is None:
                candidate = _FusionCandidate(
                    result=result
                )

                candidates[
                    result.chunk_id
                ] = candidate

            candidate.vector_rank = rank

            candidate.vector_score = (
                result.score
            )

            candidate.rrf_score += (
                1.0 / (RRF_K + rank)
            )
        
        for rank , result in enumerate(
            bm25_results,
            start=1,
        ):
            candidate = candidates.get(
                result.chunk_id
            )

            if candidate is None:
                candidate = _FusionCandidate(
                    result=result
                )

                candidates[
                    result.chunk_id
                ] = candidate

            candidate.bm25_rank = rank
            candidate.bm25_score = (
                result.score
            )

            candidate.rrf_score += (
                1.0
                / (
                    RRF_K
                    + rank
                )
            )
        ranked_candidates = sorted(
            candidates.values(),
            key=lambda candidate: candidate.rrf_score,
            reverse=True
        )

        final_results : list[RetrievalResult] = []

        for candidate in (
            ranked_candidates[
                :final_top_k
            ]
        ):

            base = candidate.result

            final_results.append(
                RetrievalResult(
                    chunk_id=(
                        base.chunk_id
                    ),
                    document_id=(
                        base.document_id
                    ),
                    document_code=(
                        base.document_code
                    ),
                    document_type=(
                        base.document_type
                    ),
                    version_label=(
                        base.version_label
                    ),
                    chunk_index=(
                        base.chunk_index
                    ),
                    section_number=(
                        base.section_number
                    ),
                    section_title=(
                        base.section_title
                    ),
                    content=(
                        base.content
                    ),
                    source_filename=(
                        base.source_filename
                    ),
                    score=round(
                        candidate.rrf_score,
                        6,
                    ),
                    retrieval_method=(
                        "hybrid"
                    ),
                    vector_rank=(
                        candidate.vector_rank
                    ),
                    bm25_rank=(
                        candidate.bm25_rank
                    ),
                    vector_score=(
                        candidate.vector_score
                    ),
                    bm25_score=(
                        candidate.bm25_score
                    ),
                )
            )

        return final_results