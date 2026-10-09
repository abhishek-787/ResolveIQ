from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.models.enums import (
    DocumentStatus,
    DocumentType,
)


class KnowledgeDocumentResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    document_code: str

    original_filename: str

    document_type: DocumentType

    status: DocumentStatus

    file_size_bytes: int

    uploaded_at: datetime

    processed_at: datetime | None

    error_message: str | None

    extracted_char_count: int | None

    page_count: int | None

class DocumentPreviewResponse(
    BaseModel
):
    document_code: str
    original_filename: str
    status: DocumentStatus

    preview: str

    extracted_char_count: int | None
    page_count: int | None


class KnowledgeChunkResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    chunk_index: int

    document_type: str

    source_filename: str

    section_number: str | None

    section_title: str

    content: str

    char_count: int


class ChunkDocumentResponse(
    BaseModel
):
    document_code: str

    status: DocumentStatus

    chunk_count: int

    section_count: int