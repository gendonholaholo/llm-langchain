"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str = ""

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_bot"

    # WAHA
    waha_api_url: str = "http://localhost:3000"
    waha_api_key: str = ""
    waha_session: str = "default"

    # Booking API
    booking_api_url: str = "http://localhost:8080"
    booking_api_key: str = ""

    # App
    log_level: str = "INFO"
    environment: str = "development"

    @property
    def sync_database_url(self) -> str:
        """Return a synchronous database URL for Alembic."""
        return self.database_url.replace("+asyncpg", "")


settings = Settings()
