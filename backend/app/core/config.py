from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "ResolveIQ"

    app_version: str = "0.1.0"

    environment: str = "development"

    database_url: str

    ollama_base_url: str = "http://192.168.0.3:11434"

    embedding_model: str = "nomic-embed-text:latest"

    reasoning_model: str = "gemma4:31b-cloud"

    vision_model: str = "qwen3-vl:4b"

    support_image_dir: str = (
        "storage/support_images"
    )

    max_support_image_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()