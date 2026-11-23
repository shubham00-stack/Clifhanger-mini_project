"""Environment configuration loaded securely from environment and .env."""

import os
from functools import lru_cache
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # Application & Environment
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "production"))
    app_port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8000")))
    app_host: str = Field(default_factory=lambda: os.getenv("APP_HOST", "0.0.0.0"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Security & Limits
    max_payload_bytes: int = Field(default_factory=lambda: int(os.getenv("MAX_PAYLOAD_BYTES", "10485760"))) # 10 MB
    cors_allowed_origins: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if origin.strip()
        ]
    )

    # NVIDIA NIM Provider Settings
    nvidia_api_key: str = Field(default_factory=lambda: os.getenv("NVIDIA_API_KEY", ""))
    nvidia_base_url: str = Field(default_factory=lambda: os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))

    # Configurable NVIDIA NIM Models (Section 4.2)
    model_primary_narrative: str = Field(
        default_factory=lambda: os.getenv("MODEL_PRIMARY_NARRATIVE", "nvidia/nemotron-3-nano-omni-30b-a3b-instruct")
    )
    model_fast_text: str = Field(
        default_factory=lambda: os.getenv("MODEL_FAST_TEXT", "nvidia/nemotron-3.5-bolt-e4b")
    )
    model_embeddings: str = Field(
        default_factory=lambda: os.getenv("MODEL_EMBEDDINGS", "nvidia/nemotron-3.5-embed-1b")
    )
    model_reranker: str = Field(
        default_factory=lambda: os.getenv("MODEL_RERANKER", "nvidia/nemotron-3.5-rerank-8b")
    )
    model_ocr_parser: str = Field(
        default_factory=lambda: os.getenv("MODEL_OCR_PARSER", "nvidia/nemotron-3.5-parse")
    )

    # Resilience & Retries
    max_retries: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    retry_base_delay: float = Field(default_factory=lambda: float(os.getenv("RETRY_BASE_DELAY", "0.5")))
    retry_max_delay: float = Field(default_factory=lambda: float(os.getenv("RETRY_MAX_DELAY", "4.0")))


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
