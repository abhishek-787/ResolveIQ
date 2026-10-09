import re

from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.repositories.knowledge import (
    list_active_knowledge_chunks,
)
from app.retrieval.types import (
    RetrievalResult,
)

from app.models.enums import (
    DocumentType,
)

def _tokenize(
        text:str,
)-> list[str]:

    text = text.lower()

    text = re.sub(
        r"(?<=\d),(?=\d)",
        "",
        text,
    )

    tokens = re.findall(
        r"[a-z0-9]+(?:-[a-z0-9]+)*",
        text,
    )

    return tokens

class BM25Retriever:

    def __init__(self,default_top_k: int = 8,):

        self.default_top_k = (
            default_top_k
        )

    def retrieve(
        self,
        db: Session,
        query: str,
        top_k: int | None = None,
        document_types: list[DocumentType] | None = None,
    )-> list[RetrievalResult]:

        query = query.strip()

        if not query:
            return []

        query_tokens = _tokenize(
            query
        )

        if not query_tokens:
            return []

        rows = (
            list_active_knowledge_chunks(
                db,
                document_types=document_types,
            )
        )

        if not rows:
            return []

        tokenized_corpus = [
            _tokenize(
                chunk.content
            )
            for chunk, _ in rows
        ]

        bm25 = BM25Okapi(
            tokenized_corpus
        )

        scores = bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        limit = (
            top_k
            if top_k is not None
            else self.default_top_k
        )

        results : list[RetrievalResult] = []

        for index in ranked_indices:

            score = float(
                scores[index]
            )

            if score <= 0:
                continue

            chunk, document = (
                rows[index]
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
                        document.version_label
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
                        score,
                        4,
                    ),
                    retrieval_method=(
                        "bm25"
                    ),
                )
            )

            if len(results) >= limit:
                break

        return results

        
