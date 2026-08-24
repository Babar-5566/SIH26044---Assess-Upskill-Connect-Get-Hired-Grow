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
    ai_provider: str = "gemini"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.5-flash"
    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = "openai/gpt-4o-mini"
    ai_timeout_seconds: float = 20.0
    ai_max_retries: int = 2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        return v.split(",") if isinstance(v, str) else v
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
