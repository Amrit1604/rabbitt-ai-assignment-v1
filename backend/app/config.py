from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    GEMINI_API_KEY: str
    GROQ_API_KEY: str

    # Email (Gmail SMTP with App Password)
    GMAIL_USER: str
    GMAIL_APP_PASSWORD: str
    # SendGrid API key (fallback)
    SENDGRID_API_KEY: str | None = None

    # Security — used to restrict CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # File upload limit in megabytes
    MAX_FILE_MB: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance. Call this everywhere instead of Settings()."""
    return Settings()
