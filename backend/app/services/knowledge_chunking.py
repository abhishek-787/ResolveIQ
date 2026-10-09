from sqlalchemy.orm import (
    Session,
)

from app.models.enums import (
    DocumentStatus,
)
from app.models.knowledge import (
    KnowledgeChunk,
)
from app.repositories.knowledge import (
    get_document_by_code,
    list_document_chunks,
    replace_document_chunks,
    save_document,
)
from app.services.document_chunker import (
    chunk_document_text,
)


class DocumentChunkingError(
    ValueError
):
    pass


class DocumentNotFoundError(
    ValueError
):
    pass


def chunk_knowledge_document(
    db: Session,
    document_code: str,
) -> tuple[
    object,
    list[KnowledgeChunk],
]:

    document = (
        get_document_by_code(
            db,
            document_code,
        )
    )

    if document is None:
        raise DocumentNotFoundError(
            "Knowledge document "
            "was not found."
        )

    if not document.extracted_text:
        raise DocumentChunkingError(
            "Document must be "
            "processed before chunking."
        )

    drafts = chunk_document_text(
        document.extracted_text
    )

    database_chunks: list[
        KnowledgeChunk
    ] = []

    for (
        chunk_index,
        draft,
    ) in enumerate(
        drafts
    ):

        database_chunks.append(
            KnowledgeChunk(
                document_id=(
                    document.id
                ),
                chunk_index=(
                    chunk_index
                ),
                document_type=(
                    document
                    .document_type
                    .value
                ),
                source_filename=(
                    document
                    .original_filename
                ),
                section_number=(
                    draft
                    .section_number
                ),
                section_title=(
                    draft
                    .section_title
                ),
                content=(
                    draft.content
                ),
                char_count=(
                    draft.char_count
                ),
                content_hash=(
                    draft.content_hash
                ),
            )
        )

    stored_chunks = (
        replace_document_chunks(
            db=db,
            document_id=document.id,
            chunks=database_chunks,
        )
    )

    document.status = (
        DocumentStatus.CHUNKED
    )

    document.error_message = None

    save_document(
        db,
        document,
    )

    return (
        document,
        stored_chunks,
    )


def get_knowledge_document_chunks(
    db: Session,
    document_code: str,
) -> tuple[
    object,
    list[KnowledgeChunk],
]:

    document = (
        get_document_by_code(
            db,
            document_code,
        )
    )

    if document is None:
        raise DocumentNotFoundError(
            "Knowledge document "
            "was not found."
        )

    chunks = (
        list_document_chunks(
            db,
            document.id,
        )
    )

    return (
        document,
        chunks,
    )