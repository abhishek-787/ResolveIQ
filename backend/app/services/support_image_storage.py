from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

def _get_image_storage_dir() -> Path:

    storage_dir = Path(
        settings.support_image_dir
    )

    storage_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return storage_dir

def _validate_image_file(
    file: UploadFile,
) -> str:

    original_name = (
        file.filename
        or ""
    )

    extension = (
        Path(original_name)
        .suffix
        .lower()
    )

    if (
        extension
        not in ALLOWED_IMAGE_EXTENSIONS
    ):
        raise ValueError(
            "Unsupported image type. "
            "Use JPG, JPEG, PNG, or WEBP."
        )

    if (
        file.content_type
        not in ALLOWED_CONTENT_TYPES
    ):
        raise ValueError(
            "Unsupported image content type."
        )

    return extension


async def save_support_image(
    file: UploadFile,
) -> Path:

    extension = (
        _validate_image_file(
            file
        )
    )

    content = await file.read()

    max_bytes = (
        settings.max_support_image_mb
        * 1024
        * 1024
    )

    if not content:
        raise ValueError(
            "Uploaded image is empty."
        )

    if len(content) > max_bytes:
        raise ValueError(
            f"Image exceeds "
            f"{settings.max_support_image_mb} MB."
        )

    storage_dir = (
        _get_image_storage_dir()
    )

    stored_name = (
        f"{uuid4().hex}"
        f"{extension}"
    )

    stored_path = (
        storage_dir
        / stored_name
    )

    stored_path.write_bytes(
        content
    )

    return stored_path