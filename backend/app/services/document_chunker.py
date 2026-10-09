import hashlib
import re
from dataclasses import (
    dataclass,
)


MAX_CHUNK_CHARS = 1400
CHUNK_OVERLAP_CHARS = 180


SECTION_PATTERN = re.compile(
    r"^(?P<number>\d+(?:\.\d+)*)\.\s+"
    r"(?P<title>.+)$"
)


@dataclass(
    frozen=True
)
class ChunkDraft:
    section_number: str | None
    section_title: str

    content: str
    char_count: int
    content_hash: str


def _content_hash(
    content: str,
) -> str:

    return hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()


def _split_sections(
    text: str,
) -> list[
    tuple[
        str | None,
        str,
        str,
    ]
]:

    sections: list[
        tuple[
            str | None,
            str,
            str,
        ]
    ] = []

    current_number: (
        str | None
    ) = None

    current_title = (
        "Document Information"
    )

    current_lines: list[str] = []

    for raw_line in (
        text.splitlines()
    ):

        line = raw_line.strip()

        match = (
            SECTION_PATTERN
            .match(line)
        )

        if match:

            body = "\n".join(
                current_lines
            ).strip()

            if body:
                sections.append(
                    (
                        current_number,
                        current_title,
                        body,
                    )
                )

            current_number = (
                match.group(
                    "number"
                )
            )

            current_title = (
                match.group(
                    "title"
                ).strip()
            )

            current_lines = []

            continue

        current_lines.append(
            line
        )

    body = "\n".join(
        current_lines
    ).strip()

    if body:
        sections.append(
            (
                current_number,
                current_title,
                body,
            )
        )

    return sections


def _split_with_overlap(
    text: str,
    max_chars: int,
    overlap_chars: int,
) -> list[str]:

    if len(text) <= max_chars:
        return [
            text.strip()
        ]

    pieces: list[str] = []

    start = 0

    while start < len(text):

        end = min(
            start + max_chars,
            len(text),
        )

        if end < len(text):

            search_start = (
                start
                + (max_chars // 2)
            )

            candidates = [
                text.rfind(
                    "\n\n",
                    search_start,
                    end,
                ),
                text.rfind(
                    "\n",
                    search_start,
                    end,
                ),
                text.rfind(
                    ". ",
                    search_start,
                    end,
                ),
            ]

            boundary = max(
                candidates
            )

            if boundary > start:
                end = (
                    boundary + 1
                )

        piece = text[
            start:end
        ].strip()

        if piece:
            pieces.append(
                piece
            )

        if end >= len(text):
            break

        next_start = max(
            end - overlap_chars,
            start + 1,
        )

        start = next_start

    return pieces


def chunk_document_text(
    text: str,
) -> list[ChunkDraft]:

    cleaned_text = (
        text.strip()
    )

    if not cleaned_text:
        raise ValueError(
            "Document text "
            "cannot be empty."
        )

    sections = (
        _split_sections(
            cleaned_text
        )
    )

    chunks: list[
        ChunkDraft
    ] = []

    for (
        section_number,
        section_title,
        section_body,
    ) in sections:

        if section_number:
            heading = (
                f"{section_number}. "
                f"{section_title}"
            )
        else:
            heading = (
                section_title
            )

        available_chars = max(
            400,
            MAX_CHUNK_CHARS
            - len(heading)
            - 2,
        )

        body_parts = (
            _split_with_overlap(
                text=section_body,
                max_chars=(
                    available_chars
                ),
                overlap_chars=(
                    CHUNK_OVERLAP_CHARS
                ),
            )
        )

        for body_part in (
            body_parts
        ):

            content = (
                f"{heading}\n\n"
                f"{body_part}"
            ).strip()

            chunks.append(
                ChunkDraft(
                    section_number=(
                        section_number
                    ),
                    section_title=(
                        section_title
                    ),
                    content=content,
                    char_count=len(
                        content
                    ),
                    content_hash=(
                        _content_hash(
                            content
                        )
                    ),
                )
            )

    if not chunks:
        raise ValueError(
            "No chunks could be "
            "created from document."
        )

    return chunks