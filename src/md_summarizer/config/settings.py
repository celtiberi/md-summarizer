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
    env_file = os.path.join(os.getcwd(), ".env")
    
    # Load environment file
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    else:
        # Log warning but don't fail - environment variables might be set directly
        import logging
        logging.warning(f"Environment file not found: {env_file}")
    
    return Settings() 