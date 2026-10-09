from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import (
    Session,
)

from app.db.session import (
    get_db,
)
from app.models.enums import (
    DocumentType,
)
from app.repositories.knowledge import (
    list_documents,
    get_document_by_code,
)
from app.schemas.knowledge import (
    ChunkDocumentResponse,
    DocumentPreviewResponse,
    KnowledgeChunkResponse,
    KnowledgeDocumentResponse,
)
from app.services.document_extractor import (
    DocumentExtractionError,
)

from app.services.knowledge_ingestion import (
    DocumentNotFoundError,
    InvalidDocumentError,
    process_knowledge_document,
    upload_knowledge_document,
)

from app.services.knowledge_chunking import (
    DocumentChunkingError,
    DocumentNotFoundError as ChunkDocumentNotFoundError,
    chunk_knowledge_document,
    get_knowledge_document_chunks,
)

from app.services.knowledge_indexing import (
    DocumentIndexingError,
    DocumentNotFoundError
    as IndexDocumentNotFoundError,
    index_knowledge_document,
)

from app.services.knowledge_search import (
    search_knowledge,
)

router = APIRouter(
    prefix="/admin/documents",
    tags=["Admin Knowledge"],
)


@router.post(
    "/upload",
    response_model=KnowledgeDocumentResponse,
    status_code=201,
)
async def upload_document(
    document_type: DocumentType = Form(...),
    document_key: str | None = Form(None),
    version_label: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        return await upload_knowledge_document(
            db=db,
            file=file,
            document_type=document_type,
            document_key=document_key,
            version_label=version_label,
        )

    except InvalidDocumentError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[
        KnowledgeDocumentResponse
    ],
)
def get_documents(
    db: Session = Depends(get_db),
):
    return list_documents(
        db
    )


@router.post(
    "/{document_code}/process",
    response_model=(
        KnowledgeDocumentResponse
    ),
)
def process_document(
    document_code: str,
    db: Session = Depends(get_db),
):
    try:
        return process_knowledge_document(
            db,
            document_code,
        )

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

@router.get(
    "/{document_code}/preview",
    response_model=(
        DocumentPreviewResponse
    ),
)
def preview_document(
    document_code: str,
    db: Session = Depends(get_db),
):
    document = (
        get_document_by_code(
            db,
            document_code,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Knowledge document "
                "was not found."
            ),
        )

    text = (
        document.extracted_text
        or ""
    )

    return DocumentPreviewResponse(
        document_code=(
            document.document_code
        ),
        original_filename=(
            document.original_filename
        ),
        status=document.status,
        preview=text[:2000],
        extracted_char_count=(
            document.extracted_char_count
        ),
        page_count=(
            document.page_count
        ),
    )

@router.post(
    "/{document_code}/chunk",
    response_model=(
        ChunkDocumentResponse
    ),
)
def chunk_document(
    document_code: str,
    db: Session = Depends(get_db),
):

    try:
        (
            document,
            chunks,
        ) = chunk_knowledge_document(
            db,
            document_code,
        )

        unique_sections = {
            (
                chunk.section_number,
                chunk.section_title,
            )
            for chunk in chunks
        }

        return ChunkDocumentResponse(
            document_code=(
                document.document_code
            ),
            status=(
                document.status
            ),
            chunk_count=len(
                chunks
            ),
            section_count=len(
                unique_sections
            ),
        )

    except ChunkDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except DocumentChunkingError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get(
    "/{document_code}/chunks",
    response_model=list[
        KnowledgeChunkResponse
    ],
)
def get_document_chunks(
    document_code: str,
    db: Session = Depends(get_db),
):

    try:
        (
            _,
            chunks,
        ) = (
            get_knowledge_document_chunks(
                db,
                document_code,
            )
        )

        return chunks

    except ChunkDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

@router.post(
    "/{document_code}/index",
    response_model=KnowledgeDocumentResponse,
)
def index_document(
    document_code: str,
    db: Session = Depends(get_db),
):
    try:
        return index_knowledge_document(
            db,
            document_code,
        )

    except IndexDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except DocumentIndexingError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get(
    "/search",
)
def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
):
    return search_knowledge(
        db=db,
        query=query,
        top_k=top_k,
    )


@router.post(
    "/ingest",
    response_model=KnowledgeDocumentResponse,
    status_code=201,
)
async def ingest_document(
    document_type: DocumentType = Form(...),
    document_key: str = Form(...),
    version_label: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        document = (
            await upload_knowledge_document(
                db=db,
                file=file,
                document_type=document_type,
                document_key=document_key,
                version_label=version_label,
            )
        )

        process_knowledge_document(
            db,
            document.document_code,
        )

        chunk_knowledge_document(
            db,
            document.document_code,
        )

        indexed_document = (
            index_knowledge_document(
                db,
                document.document_code,
            )
        )

        return indexed_document

    except InvalidDocumentError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc