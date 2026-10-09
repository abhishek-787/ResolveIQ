from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import DocumentStatus
from app.repositories.knowledge import (
    activate_document_version,
    get_document_by_code,
    list_document_chunks,
    save_document,
    save_indexed_document,
)
from app.services.embedding_service import (
    embed_texts,
)


class DocumentIndexingError(
    ValueError
):
    pass


class DocumentNotFoundError(
    ValueError
):
    pass

def index_knowledge_document(
        db:Session,
        document_code: str,
):
    document = get_document_by_code(
        db,
        document_code,
    )

    if document is None:
        raise DocumentNotFoundError(
            "Knowledge document was not found."
        )

    chunks = list_document_chunks(
        db,
        document.id
    )

    if not chunks:
        raise DocumentIndexingError(
            "Document must be chunked "
            "before indexing."
        )

    texts = [
        chunk.content
        for chunk in chunks
    ]

    try:
        vectors = embed_texts(texts)

        if len(vectors)!=len(chunks):
            raise DocumentIndexingError(
                "Embedding count does not "
                "match chunk count."
            )

        now = datetime.now(
            timezone.utc
        )

        for chunk,vector in zip(
            chunks,
            vectors,
            strict=True,
        ):
            chunk.embedding = vector

            chunk.embedding_model = (
                settings.embedding_model
            )

            chunk.embedded_at = now

        document.status = (
            DocumentStatus.INDEXED
        )

        document.error_message = None
        document.processed_at = now

        activate_document_version(
            db,
            document
        )

        return save_indexed_document(
            db,
            document,
            chunks,
        )

    except Exception as exc:
        db.rollback()

        document.status = (
            DocumentStatus.FAILED
        )

        document.error_message = str(exc)

        save_document(
            db,
            document,
        )

        raise

