from dataclasses import dataclass


@dataclass
class RetrievalResult:
    chunk_id: int
    document_id: int

    document_code: str
    document_type: str
    version_label: str | None

    chunk_index: int

    section_number: str | None
    section_title: str

    content: str
    source_filename: str

    score: float

    retrieval_method: str

    vector_rank: int | None = None
    bm25_rank: int | None = None

    vector_score: float | None = None
    bm25_score: float | None = None

    query_hits: int | None = None

    rerank_rank: int | None = None

@dataclass
class EvidenceCitation:
    citation_id: str

    chunk_id: int

    document_code: str
    document_type: str
    version_label: str | None

    section_number: str | None
    section_title: str

    source_filename: str
    content: str

    rank: int