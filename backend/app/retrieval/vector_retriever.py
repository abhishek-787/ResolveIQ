from sqlalchemy.orm import Session

from app.repositories.knowledge import (
    semantic_search_chunks,
)
from app.retrieval.types import (
    RetrievalResult,
)
from app.services.embedding_service import (
    embed_query,
)

from app.models.enums import (
    DocumentType,
)


class VectorRetriever:

    def __init__(
        self,
        default_top_k: int = 8,
    ):
        self.default_top_k = (
            default_top_k
        )

    def retrieve(
    self,
    db: Session,
    query: str,
    top_k: int | None = None,
    document_types: list[
        DocumentType
    ] | None = None,
) -> list[RetrievalResult]:

        query = query.strip()

        if not query:
            return []

        limit = (
            top_k
            if top_k is not None
            else self.default_top_k
        )

        query_embedding = (
            embed_query(
                query
            )
        )

        rows = semantic_search_chunks(
            db=db,
            query_embedding=query_embedding,
            limit=limit,
            document_types=document_types,
)

        results: list[
            RetrievalResult
        ] = []

        for (
            chunk,
            document,
            distance,
        ) in rows:

            similarity = (
                1.0
                - float(distance)
            )

            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=(
                        document.id
                    ),
                    document_code=(
                        document.document_code
                    ),
                    document_type=(
                        document
                        .document_type
                        .value
                    ),
                    version_label=(
                        document
                        .version_label
                    ),
                    chunk_index=(
                        chunk.chunk_index
                    ),
                    section_number=(
                        chunk.section_number
                    ),
                    section_title=(
                        chunk.section_title
                    ),
                    content=(
                        chunk.content
                    ),
                    source_filename=(
                        chunk.source_filename
                    ),
                    score=round(
                        similarity,
                        4,
                    ),
                    retrieval_method=(
                        "vector"
                    ),
                )
            )

        return results