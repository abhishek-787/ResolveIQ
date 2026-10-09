from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.retrieval.metadata_filter import (
    document_types_for_intent,
)
from app.retrieval.multi_query import (
    generate_search_queries,
)
from app.retrieval.multi_query_retriever import (
    MultiQueryRetriever,
)
from app.retrieval.query_rewriter import (
    QueryRewriteResult,
    rewrite_query,
)
from app.retrieval.reranker import (
    rerank_results,
)
from app.retrieval.types import (
    RetrievalResult,
)


@dataclass
class AdvancedRetrievalResult:
    rewrite: QueryRewriteResult

    search_queries: list[str]

    applied_document_types: list[str]

    results: list[
        RetrievalResult
    ]


class AdvancedRetriever:

    def __init__(self):
        self.multi_query_retriever = (
            MultiQueryRetriever()
        )

    def retrieve(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
    ) -> AdvancedRetrievalResult:


        rewrite = rewrite_query(
            query
        )


        document_types = (
            document_types_for_intent(
                rewrite.intent
            )
        )

        search_queries = (
            generate_search_queries(
                rewritten_query=(
                    rewrite.rewritten_query
                ),
                intent=rewrite.intent,
            )
        )

        candidate_k = min(
            max(
                top_k * 2,
                10,
            ),12
        )

        candidates = (
            self.multi_query_retriever
            .retrieve(
                db=db,
                queries=search_queries,
                top_k=candidate_k,
                document_types=(
                    document_types
                ),
            )
        )

        final_results = rerank_results(
            original_query=query,
            rewritten_query=(
                rewrite.rewritten_query
            ),
            candidates=candidates,
            top_k=top_k,
        )

        applied_types = (
            [
                item.value
                for item in document_types
            ]
            if document_types
            else []
        )

        return AdvancedRetrievalResult(
            rewrite=rewrite,
            search_queries=search_queries,
            applied_document_types=(
                applied_types
            ),
            results=final_results,
        )