from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.models.enums import (
    DocumentStatus,
    DocumentType,
)

from pgvector.sqlalchemy import Vector


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    document_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    file_extension: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(
            DocumentType,
            name="document_type",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(
            DocumentStatus,
            name="document_status",
        ),
        nullable=False,
        default=DocumentStatus.UPLOADED,
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extracted_text: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    extracted_char_count: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    page_count: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    document_key: Mapped[str | None] = mapped_column(
    String(120),
    nullable=True,
    index=True,
)

    version_label: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    supersedes_document_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "knowledge_documents.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    chunks = relationship(
        "KnowledgeChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="KnowledgeChunk.chunk_index",
    )

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "knowledge_documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    section_number: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    section_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    char_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    embedding: Mapped[
        list[float] | None
    ] = mapped_column(
        Vector(768),
        nullable=True,
    )

    embedding_model: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
    )

    embedded_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    document = relationship(
        "KnowledgeDocument",
        back_populates="chunks",
    )