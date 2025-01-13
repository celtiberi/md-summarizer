import os
from functools import lru_cache
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pydantic import field_validator

# Get project root directory (one level up from src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

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
    
    if env:
        # Use environment-specific file (.env.development, .env.test, etc)
        env_type = EnvironmentType(env)
        env_file = os.path.join(PROJECT_ROOT, f".env.{env_type.value}")
    else:
        # Default to .env
        env_file = os.path.join(PROJECT_ROOT, ".env")
        env_type = EnvironmentType.DEVELOPMENT
    
    # Load environment file
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    else:
        raise FileNotFoundError(f"Environment file not found: {env_file}")
    
    return Settings(env=env_type) 