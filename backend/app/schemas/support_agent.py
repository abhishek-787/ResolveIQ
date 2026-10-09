from pydantic import (
    BaseModel,
    Field,
)


class SupportRequest(BaseModel):

    query: str = Field(
        min_length=2,
    )

    conversation_id: int | None = None


class SupportSource(BaseModel):

    citation_id: str

    document_code: str
    document_type: str

    version_label: str | None

    section_title: str
    source_filename: str


class SupportResponse(BaseModel):

    conversation_id: int

    answer: str

    sources: list[
        SupportSource
    ]