from app.retrieval.types import (
    EvidenceCitation,
    RetrievalResult,
)

def build_citations(
        results: list[RetrievalResult],
) -> list[EvidenceCitation]:

    citations = []

    for rank, result in enumerate(
        results,
        start=1,
    ):
        citations.append(
            EvidenceCitation(
                citation_id=f"S{rank}",

                chunk_id=result.chunk_id,

                document_code=(
                    result.document_code
                ),

                document_type=(
                    result.document_type
                ),

                version_label=(
                    result.version_label
                ),

                section_number=(
                    result.section_number
                ),

                section_title=(
                    result.section_title
                ),

                source_filename=(
                    result.source_filename
                ),

                content=result.content,

                rank=rank,
            )
        )

    return citations