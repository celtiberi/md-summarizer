import os
from functools import lru_cache
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pydantic import field_validator

# Get project root (two levels up from config)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class EnvironmentType(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    env: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    openai_api_key: str
    model: str = "gpt-3.5-turbo"
    provider: str = "openai"  # openai, anthropic, or google
    log_level: str = "INFO"    
    
    @property
    def is_production(self) -> bool:
        return self.env == EnvironmentType.PRODUCTION
    
    @property
    def is_test(self) -> bool:
        return self.env == EnvironmentType.TEST
    
    @property
    def env_file_path(self) -> str:
        """Get the environment file path based on current environment"""
        return os.path.join(PROJECT_ROOT, f".env.{self.env.value}")

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Check for ENV, default to using .env if not set
    env = os.getenv("ENV")
    env_type = EnvironmentType.DEVELOPMENT
    
    if env:
        # Use environment-specific file (.env.development, .env.test, etc)
        env_type = EnvironmentType(env)
        env_file = os.path.join(PROJECT_ROOT, f".env.{env_type.value}")
        # Fall back to .env if environment-specific file doesn't exist
        if not os.path.exists(env_file):
            env_file = os.path.join(os.getcwd(), ".env")
    else:
        # Default to .env in current directory
        env_file = os.path.join(os.getcwd(), ".env")
    
    # Load environment file
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    else:
        # Log warning but don't fail - environment variables might be set directly
        import logging
        logging.warning(f"Environment file not found: {env_file}")
    
    return Settings(env=env_type) 