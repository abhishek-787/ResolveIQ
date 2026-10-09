from sqlalchemy.orm import Session

from app.repositories.knowledge import (
    semantic_search_chunks,
)
from app.services.embedding_service import (
    embed_query,
)

def search_knowledge(
    db: Session,
    query: str,
    top_k: int = 5,
):
    query_vector = embed_query(
        query
    )

    rows = semantic_search_chunks(
        db=db,
        query_embedding=query_vector,
        limit=top_k
    )

    results = []

    for chunk , distance in rows:
        similarity = (
            1 - float(distance)
        )

        results.append(
            {
                "chunk_index":
                    chunk.chunk_index,

                "document_type":
                    chunk.document_type,

                "source_filename":
                    chunk.source_filename,

                "section_number":
                    chunk.section_number,

                "section_title":
                    chunk.section_title,

                "content":
                    chunk.content,

                "similarity":
                    round(
                        similarity,
                        4,
                    ),
            }
        )

    return results