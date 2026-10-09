from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import (
    Session,
)

from app.models.knowledge import (
    KnowledgeChunk,
    KnowledgeDocument,
)

from sqlalchemy import (
    delete,
    select,
)

from app.models.enums import (
    DocumentStatus,
    DocumentType,
)

def create_document(
        db:Session,
        document: KnowledgeDocument,
)->KnowledgeDocument:
    db.add(
        document
    )
    db.commit()
    db.refresh(
        document
    )
    return document

def get_document_by_code(
        db:Session,
        document_code:str,
)-> KnowledgeDocument | None :
    statement = (
        select(KnowledgeDocument).where(KnowledgeDocument.document_code == document_code)
    )
    return db.scalar(
        statement
    )

def list_documents(
        db:Session,
)->list[KnowledgeDocument]:
    statement = (
        select(KnowledgeDocument).order_by(KnowledgeDocument.uploaded_at.desc())
    )
    return list(
        db.scalars(
        statement
    )
    )

def save_document(
    db: Session,
    document: KnowledgeDocument,
) -> KnowledgeDocument:

    db.add(
        document
    )

    db.commit()

    db.refresh(
        document
    )

    return document


def replace_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[
        KnowledgeChunk
    ],
) -> list[
    KnowledgeChunk
]:

    try:
        db.execute(
            delete(
                KnowledgeChunk
            )
            .where(
                KnowledgeChunk.document_id
                == document_id
            )
        )

        db.add_all(
            chunks
        )

        db.commit()

        for chunk in chunks:
            db.refresh(
                chunk
            )

        return chunks

    except Exception:
        db.rollback()
        raise


def list_document_chunks(
    db: Session,
    document_id: int,
) -> list[
    KnowledgeChunk
]:

    statement = (
        select(
            KnowledgeChunk
        )
        .where(
            KnowledgeChunk.document_id
            == document_id
        )
        .order_by(
            KnowledgeChunk.chunk_index
        )
    )

    return list(
        db.scalars(
            statement
        )
    )

def activate_document_version(
    db: Session,
    document: KnowledgeDocument,
) -> None:

    if not document.document_key:
        document.is_active = True
        return

    statement = (
        select(KnowledgeDocument)
        .where(
            KnowledgeDocument.document_key
            == document.document_key,
            KnowledgeDocument.id
            != document.id,
            KnowledgeDocument.is_active
            .is_(True),
            KnowledgeDocument.status
            == DocumentStatus.INDEXED,
        )
        .order_by(
            KnowledgeDocument.uploaded_at.desc()
        )
    )

    previous_document = db.scalar(
        statement
    )

    if previous_document:
        previous_document.is_active = False

        document.supersedes_document_id = (
            previous_document.id
        )

    document.is_active = True


def save_indexed_document(
    db: Session,
    document: KnowledgeDocument,
    chunks: list[KnowledgeChunk],
) -> KnowledgeDocument:

    try:
        db.add_all(chunks)
        db.add(document)

        db.commit()

        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise

def semantic_search_chunks(
    db: Session,
    query_embedding: list[float],
    limit: int = 10,
    document_types: list[
        DocumentType
    ] | None = None,
):

    distance = (
        KnowledgeChunk.embedding
        .cosine_distance(
            query_embedding
        )
        .label("distance")
    )

    filters = [
        KnowledgeChunk.embedding
        .is_not(None),

        KnowledgeDocument.status
        == DocumentStatus.INDEXED,

        KnowledgeDocument.is_active
        .is_(True),
    ]

    if document_types:
        filters.append(
            KnowledgeDocument.document_type
            .in_(document_types)
        )

    statement = (
        select(
            KnowledgeChunk,
            KnowledgeDocument,
            distance,
        )
        .join(
            KnowledgeDocument,
            KnowledgeChunk.document_id
            == KnowledgeDocument.id,
        )
        .where(
            *filters
        )
        .order_by(distance)
        .limit(limit)
    )

    return list(
        db.execute(
            statement
        ).all()
    )

def list_active_knowledge_chunks(
    db: Session,
    document_types: list[
        DocumentType
    ] | None = None,
):

    filters = [
        KnowledgeDocument.status
        == DocumentStatus.INDEXED,

        KnowledgeDocument.is_active
        .is_(True),
    ]

    if document_types:
        filters.append(
            KnowledgeDocument.document_type
            .in_(document_types)
        )

    statement = (
        select(
            KnowledgeChunk,
            KnowledgeDocument,
        )
        .join(
            KnowledgeDocument,
            KnowledgeChunk.document_id
            == KnowledgeDocument.id,
        )
        .where(
            *filters
        )
        .order_by(
            KnowledgeDocument.id,
            KnowledgeChunk.chunk_index,
        )
    )

    return list(
        db.execute(
            statement
        ).all()
    )
    




    