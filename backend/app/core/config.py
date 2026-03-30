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

    # --- Chunking ---
    chunk_size_tokens: int = 512
    chunk_overlap_tokens: int = 64
    chunk_min_tokens: int = 20

    # --- Embedding ---
    # "deterministic_stub" = local hash-based stub (no external calls, default for dev)
    # "openai" = OpenAI Embeddings API (requires llm_api_key)
    embedding_provider: str = "deterministic_stub"
    embedding_model: str = "text-embedding-3-small"
    embedding_timeout_seconds: int = 30
    embedding_max_retries: int = 3

    # --- Answer generation ---
    # "echo_stub" = returns context as answer (no LLM, default for dev)
    # "openai" = OpenAI Chat Completions (requires llm_api_key, Step 4)
    answer_provider: str = "echo_stub"
    # Minimum number of retrieved chunks required before generating an answer.
    # If fewer chunks pass the score threshold, the agent abstains.
    min_evidence_chunks: int = 1

    # --- LLM (Step 4 fills in full implementation) ---
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 60
    llm_api_key: str = ""

    # --- Ingestion ---
    max_upload_size_bytes: int = 50 * 1024 * 1024  # 50 MB
    allowed_content_types: list[str] = ["text/plain", "text/markdown", "text/x-markdown"]

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
