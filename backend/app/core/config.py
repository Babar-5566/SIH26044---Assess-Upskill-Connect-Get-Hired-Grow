from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, SecretStr

class Settings(BaseSettings):
    environment: str = "local"
    debug: bool = True
    database_url: str = "postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge"
    test_database_url: str = "postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge_test"
    secret_key: SecretStr = SecretStr("change-this-secret-key")
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    upload_dir: str = "storage"
    max_resume_size_mb: int = 5
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    auth_rate_limit_requests: int = 10
    notification_webhook_url: str | None = None
    audit_persist_enabled: bool = False
    ai_provider: str = "gemini"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.5-flash"
    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = "openai/gpt-4o-mini"
    ai_timeout_seconds: float = 20.0
    ai_max_retries: int = 2
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
        return v.split(",") if isinstance(v, str) else v
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

settings = Settings()
