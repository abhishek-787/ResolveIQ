from pathlib import Path
from uuid import uuid4

from fastapi import (
    UploadFile,
)
from sqlalchemy.orm import (
    Session,
)

from app.models.enums import (
    DocumentStatus,
    DocumentType,
)
from app.models.knowledge import (
    KnowledgeDocument,
)
from app.repositories.knowledge import (
    create_document,
)

from datetime import (
    datetime,
    timezone,
)

from app.repositories.knowledge import (
    create_document,
    get_document_by_code,
    save_document,
)

from app.services.document_extractor import (
    DocumentExtractionError,
    extract_document_text,
)

MAX_FILE_SIZE_BYTES = (
    10 * 1024 * 1024
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
}

KNOWLEDGE_STORAGE_DIR = (
    Path("storage")
    / "knowledge"
)


class InvalidDocumentError(
    ValueError
):
    pass

class DocumentNotFoundError(
    ValueError
):
    pass


async def upload_knowledge_document(
    db: Session,
    file: UploadFile,
    document_type: DocumentType,
    document_key: str | None = None,
    version_label: str | None = None,
) -> KnowledgeDocument:

    original_filename = (
        Path(
            file.filename
            or "document"
        )
        .name
    )

    extension = (
        Path(
            original_filename
        )
        .suffix
        .lower()
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise InvalidDocumentError(
            "Only PDF and TXT documents "
            "are currently supported."
        )

    contents = await file.read()

    if not contents:
        raise InvalidDocumentError(
            "Uploaded document is empty."
        )

    if (
        len(contents)
        > MAX_FILE_SIZE_BYTES
    ):
        raise InvalidDocumentError(
            "Document exceeds the "
            "10 MB upload limit."
        )

    KNOWLEDGE_STORAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    unique_id = uuid4().hex

    document_code = (
        f"DOC-{unique_id[:8].upper()}"
    )

    stored_filename = (
        f"{unique_id}{extension}"
    )

    file_path = (
        KNOWLEDGE_STORAGE_DIR
        / stored_filename
    )

    try:
        file_path.write_bytes(
            contents
        )

        document = KnowledgeDocument(
        document_code=document_code,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(file_path.resolve()),
        content_type=file.content_type,
        file_extension=extension,
        file_size_bytes=len(contents),
        document_type=document_type,
        document_key=document_key,
        version_label=version_label,
        status=DocumentStatus.UPLOADED,
    )

        return create_document(
            db,
            document,
        )

    except Exception:
        if file_path.exists():
            file_path.unlink()

        raise

def process_knowledge_document(
    db: Session,
    document_code: str,
) -> KnowledgeDocument:

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

    document.status = (
        DocumentStatus.PROCESSING
    )

    document.error_message = None

    save_document(
        db,
        document,
    )

    try:
        (
            extracted_text,
            page_count,
        ) = extract_document_text(
            file_path=document.file_path,
            extension=(
                document.file_extension
            ),
        )

        document.extracted_text = (
            extracted_text
        )

        document.extracted_char_count = (
            len(extracted_text)
        )

        document.page_count = (
            page_count
        )

        document.status = (
            DocumentStatus.EXTRACTED
        )

        document.processed_at = (
            datetime.now(
                timezone.utc
            )
        )

        return save_document(
            db,
            document,
        )

    except DocumentExtractionError as exc:

        document.status = (
            DocumentStatus.FAILED
        )

        document.error_message = str(
            exc
        )

        save_document(
            db,
            document,
        )

        raise

