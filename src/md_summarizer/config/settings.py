import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

class Settings(BaseSettings):
    """Application settings"""
    
    openai_api_key: str
    model: str = "gpt-3.5-turbo"
    provider: str = "openai"  # openai, anthropic, or google
    log_level: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    possible_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(__file__), "../..", ".env")
    ]
    
    # Try each possible path
    for env_file in possible_paths:
        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            break
    
    return Settings() 