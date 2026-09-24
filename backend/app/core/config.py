from pathlib import Path
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import AliasChoices, Field, field_validator, model_validator, SecretStr

class Settings(BaseSettings):
    environment: str = "local"
    debug: bool = False
    database_url: str = "postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge"
    test_database_url: str = "postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge_test"
    secret_key: SecretStr = Field(default=SecretStr("change-this-secret-key"), validation_alias=AliasChoices("secret_key", "jwt_secret"))
    access_token_expire_minutes: int = 60
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173", "http://localhost:3000"]
    upload_dir: str = "storage"
    max_resume_size_mb: int = 5
    profile_analysis_worker_enabled: bool = True
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    auth_rate_limit_requests: int = 10
    notification_webhook_url: str | None = None
    audit_persist_enabled: bool = False
    ai_provider: str = "gemini"
    gemini_api_key: SecretStr | None = Field(default=None, validation_alias=AliasChoices("gemini_api_key", "google_api_key"))
    gemini_model: str = "gemini-3-flash-preview"
    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = "openai/gpt-4o-mini"
    ai_timeout_seconds: float = 40.0
    ai_max_retries: int = 2

    # Multi-LLM Arena Settings
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o"
    anthropic_api_key: SecretStr | None = Field(default=None, validation_alias=AliasChoices("anthropic_api_key", "claude_api_key"))
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Enterprise RAG Settings
    rag_storage_dir: str = "storage/rag_documents"
    rag_vectors_dir: str = "storage/rag_vectors"
    rag_max_file_size_mb: int = 25
    rag_chunk_size: int = 700
    rag_chunk_overlap: int = 100
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.65
    embedding_model: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str) and value.lower() in {"release", "production", "prod", "off"}:
            return False
        return value
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v) if v.strip().startswith("[") else [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    @field_validator("database_url", "test_database_url", mode="before")
    @classmethod
    def normalize_postgres_driver(cls, value):
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value
    @property
    def DATABASE_URL(self) -> str:
        return self.database_url
    @property
    def TEST_DATABASE_URL(self) -> str:
        return self.test_database_url

    @property
    def secret_value(self) -> str:
        return self.secret_key.get_secret_value()

    def optional_secret(self, value: SecretStr | None) -> str | None:
        return value.get_secret_value() if value else None

    @model_validator(mode="after")
    def validate_production(self):
        if self.environment.lower() in {"production", "prod"}:
            secret = self.secret_value
            if len(secret) < 32 or secret.startswith(("change-", "replace-")):
                raise ValueError("Production requires a generated SECRET_KEY of at least 32 characters.")
            if self.debug:
                raise ValueError("DEBUG must be false in production.")
        return self

settings = Settings()
