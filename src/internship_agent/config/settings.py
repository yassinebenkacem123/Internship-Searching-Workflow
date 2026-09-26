from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from internship_agent.models.candidate import CandidateProfile


class Settings(BaseSettings):
    """Application settings and configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Settings (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Search Provider Settings
    search_provider: str | None = None
    search_api_key: str | None = None

    # Notion CRM Settings
    notion_token: str | None = None
    notion_database_id: str | None = None

    # Notification Settings
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Candidate Profile
    candidate: CandidateProfile = Field(default_factory=CandidateProfile)


def get_settings() -> Settings:
    """Return an application settings instance."""
    return Settings()
