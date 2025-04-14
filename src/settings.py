from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    OBSIDIAN_VAULT_PATH: str
    OPENAI_API_KEY: str
    MICROPHONE_NAME: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # Allow extra environment variables without raising errors
    }
