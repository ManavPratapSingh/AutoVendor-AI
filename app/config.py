"""
Configuration module — loads settings from .env file using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- API Keys ---
    tavily_api_key: str = ""
    openrouter_api_key: str = ""
    apitemplate_api_key: str = ""

    # --- OpenRouter Model Config ---
    openrouter_model: str = "google/gemini-2.0-flash-lite-preview-02-05:free"
    openrouter_temperature: float = 0.3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
