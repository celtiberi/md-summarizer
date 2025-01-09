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
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    
    # Markdown Parser
    default_section_size: int = 2000
    
    # Logging
    log_level: str = "INFO"
    
    # Add validation
    @field_validator("max_tokens")
    def validate_max_tokens(cls, v):
        if v <= 0:
            raise ValueError("max_tokens must be positive")
        return v
    
    # Add more specific settings
    openai_timeout: int = 30
    openai_max_retries: int = 3
    yaml_indent: int = 2
    
    # OpenAI specific settings
    openai_request_timeout: int = 30
    openai_max_tokens_per_request: int = 4000  # GPT-3.5's limit
    
    @field_validator("openai_max_tokens_per_request")
    def validate_max_tokens_per_request(cls, v):
        if v <= 0 or v > 4000:  # GPT-3.5's limit
            raise ValueError("openai_max_tokens_per_request must be between 1 and 4000")
        return v
    
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
    """Get cached settings instance"""
    env = os.getenv("ENV", "development")
    env_type = EnvironmentType(env)
    env_file = os.path.join(PROJECT_ROOT, f".env.{env_type.value}")
    
    # Load environment file
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    else:
        # Fallback to default .env
        default_env = os.path.join(PROJECT_ROOT, ".env")
        load_dotenv(default_env, override=True)
    
    return Settings(env=env_type) 