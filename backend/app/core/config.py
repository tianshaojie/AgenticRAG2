"""Application configuration via environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "AgenticRAG"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # --- Database ---
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_rag"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    # --- pgvector ---
    vector_dimension: int = 1536
    vector_distance_metric: Literal["cosine", "l2", "inner_product"] = "cosine"
    vector_index_type: Literal["hnsw", "ivfflat"] = "hnsw"
    hnsw_m: int = 16
    hnsw_ef_construction: int = 64

    # --- Retrieval ---
    retrieval_top_k: int = 10
    retrieval_score_threshold: float = 0.7

    # --- Agent ---
    max_agent_steps: int = 5

    # --- Embedding (placeholder, Step 2 fills in) ---
    embedding_model: str = "text-embedding-3-small"
    embedding_timeout_seconds: int = 30

    # --- LLM (placeholder, Step 4 fills in) ---
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 60
    llm_api_key: str = ""

    # --- Observability ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "console"] = "json"

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        return str(v)


@lru_cache
def get_settings() -> Settings:
    return Settings()
