from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.retrieval.vector_retriever import (
    VectorRetriever,
)
from app.schemas.retrieval import (
    RetrievalResultResponse,
)

from app.retrieval.bm25_retriever import (
    BM25Retriever,
)

from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)

from app.retrieval.query_rewriter import (
    rewrite_query,
)

from app.retrieval.advanced_retriever import (
    AdvancedRetriever,
)

from app.retrieval.grounded_retriever import (
    GroundedRetriever,
)

router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


vector_retriever = VectorRetriever()


bm25_retriever = BM25Retriever()

hybrid_retriever = HybridRetriever()

advanced_retriever = AdvancedRetriever()

grounded_retriever = GroundedRetriever()



@router.get(
    "/vector",
    response_model=list[
        RetrievalResultResponse
    ],
)
def vector_search(
    query: str = Query(
        ...,
        min_length=2,
    ),
    top_k: int = Query(
        8,
        ge=1,
        le=30,
    ),
    db: Session = Depends(get_db),
):

    results = (
        vector_retriever.retrieve(
            db=db,
            query=query,
            top_k=top_k,
        )
    )

    return [
        RetrievalResultResponse(
            chunk_id=result.chunk_id,
            document_code=(
                result.document_code
            ),
            document_type=(
                result.document_type
            ),
            version_label=(
                result.version_label
            ),
            chunk_index=(
                result.chunk_index
            ),
            section_number=(
                result.section_number
            ),
            section_title=(
                result.section_title
            ),
            content=result.content,
            source_filename=(
                result.source_filename
            ),
            score=result.score,
            retrieval_method=(
                result.retrieval_method
            ),
        )
        for result in results
    ]


@router.get(
    "/bm25",
    response_model=list[
        RetrievalResultResponse
    ],
)
def bm25_search(
    query: str = Query(
        ...,
        min_length=2,
    ),
    top_k: int = Query(
        8,
        ge=1,
        le=30,
    ),
    db: Session = Depends(get_db),
):

    results = (
        bm25_retriever.retrieve(
            db=db,
            query=query,
            top_k=top_k,
        )
    )

    return [
        RetrievalResultResponse(
            chunk_id=result.chunk_id,
            document_code=(
                result.document_code
            ),
            document_type=(
                result.document_type
            ),
            version_label=(
                result.version_label
            ),
            chunk_index=(
                result.chunk_index
            ),
            section_number=(
                result.section_number
            ),
            section_title=(
                result.section_title
            ),
            content=result.content,
            source_filename=(
                result.source_filename
            ),
            score=result.score,
            retrieval_method=(
                result.retrieval_method
            ),
        )
        for result in results
    ]

@router.get(
    "/hybrid",
    response_model=list[
        RetrievalResultResponse
    ],
)
def hybrid_search(
    query: str = Query(
        ...,
        min_length=2,
    ),
    top_k: int = Query(
        8,
        ge=1,
        le=30,
    ),
    db: Session = Depends(get_db),
):

    results = (
        hybrid_retriever.retrieve(
            db=db,
            query=query,
            top_k=top_k,
        )
    )

    return [
        RetrievalResultResponse(
            chunk_id=result.chunk_id,
            document_code=(
                result.document_code
            ),
            document_type=(
                result.document_type
            ),
            version_label=(
                result.version_label
            ),
            chunk_index=(
                result.chunk_index
            ),
            section_number=(
                result.section_number
            ),
            section_title=(
                result.section_title
            ),
            content=result.content,
            source_filename=(
                result.source_filename
            ),
            score=result.score,
            retrieval_method=(
                result.retrieval_method
            ),
            vector_rank=(
                result.vector_rank
            ),
            bm25_rank=(
                result.bm25_rank
            ),
            vector_score=(
                result.vector_score
            ),
            bm25_score=(
                result.bm25_score
            ),
        )
        for result in results
    ]

@router.get(
    "/rewrite",
)
def rewrite_search_query(
    query: str = Query(
        ...,
        min_length=2,
    ),
):
    result = rewrite_query(
        query
    )

    return result.model_dump()


@router.get(
    "/advanced",
)
def advanced_search(
    query: str = Query(
        ...,
        min_length=2,
    ),
    top_k: int = Query(
        5,
        ge=1,
        le=10,
    ),
    db: Session = Depends(get_db),
):

    result = (
        advanced_retriever.retrieve(
            db=db,
            query=query,
            top_k=top_k,
        )
    )

    return {
        "original_query":
            result.rewrite.original_query,

        "rewritten_query":
            result.rewrite.rewritten_query,

        "intent":
            result.rewrite.intent,

        "search_queries":
            result.search_queries,

        "applied_document_types":
            result.applied_document_types,

        "results": [
            {
                "chunk_id":
                    item.chunk_id,

                "document_code":
                    item.document_code,

                "document_type":
                    item.document_type,

                "version_label":
                    item.version_label,

                "section_number":
                    item.section_number,

                "section_title":
                    item.section_title,

                "content":
                    item.content,

                "retrieval_score":
                    item.score,

                "query_hits":
                    item.query_hits,

                "rerank_rank":
                    item.rerank_rank,

                "retrieval_method":
                    item.retrieval_method,
            }
            for item in result.results
        ],
    }


@router.get(
    "/grounded",
)
def grounded_search(
    query: str = Query(
        ...,
        min_length=2,
    ),
    top_k: int = Query(
        5,
        ge=1,
        le=10,
    ),
    db: Session = Depends(get_db),
):

    result = (
        grounded_retriever.retrieve(
            db=db,
            query=query,
            top_k=top_k,
        )
    )

    return {
        "original_query":
            result.original_query,

        "rewritten_query":
            result.rewritten_query,

        "intent":
            result.intent,

        "search_queries":
            result.search_queries,

        "applied_document_types":
            result.applied_document_types,

        "retrieval_attempts":
            result.retrieval_attempts,

        "retry_query":
            result.retry_query,

        "evidence_sufficient":
            result.evidence_sufficient,

        "assessment_reason":
            result.assessment_reason,

        "missing_information":
            result.missing_information,

        "citations": [
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
        ],
    }