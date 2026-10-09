import re
from pathlib import Path

from pypdf import (
    PdfReader,
)


class DocumentExtractionError(
    RuntimeError
):
    pass


def _clean_text(
    text: str,
) -> str:

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r" +\n",
        "\n",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()

def _extract_txt(
        file_path:Path,
) -> tuple[str,int | None ]:
    try:
        text = file_path.read_text(
            encoding="utf-8-sig"
        )
    except UnicodeDecodeError as exc:
        raise DocumentExtractionError(
            "TXT document must use "
            "UTF-8 encoding."
        ) from exc

    return(
        _clean_text(
            text
        ),None
    )

def _extract_pdf(
        file_path: Path,
)->tuple[str,int]:
    try:
        reader = PdfReader(
            str(file_path)
        )
    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to open PDF document."
        ) from exc

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise DocumentExtractionError(
                "Encrypted PDF documents "
                "are not supported."
            ) from exc

    page_texts: list[str] = []

    for page in reader.pages:
        text = (
            page.extract_text() or ""
        )

        cleaned = _clean_text(
            text
        )
        if cleaned:
            page_texts.append(
                cleaned
            )

    final_text = "\n\n".join(
        page_texts
    )

    return (
        _clean_text(
            final_text
        ),
        len(reader.pages),
    )

def extract_document_text(
        file_path:str,
        extension:str,
)-> tuple[str, int | None]:

    path = Path(
        file_path
    )

    if not path.exists():
        raise DocumentExtractionError(
            "Stored document file "
            "was not found."
        )

    if extension == ".txt":
        text, page_count = (
            _extract_txt(
                path,
            )
        )

    elif extension == ".pdf":
            text, page_count = (
                _extract_pdf(
                    path,
                )
            )

    else:
        raise DocumentExtractionError(
            "Unsupported document format."
        )

    if not text.strip():
        raise DocumentExtractionError(
            "No readable text could "
            "be extracted from document."
        )

    return (
        text,
        page_count,
    )
