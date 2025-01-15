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
    print("\n=== Debug: Loading Settings ===")
    print(f"Current working directory: {os.getcwd()}")
    
    potential_env_paths = [
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.path.dirname(__file__), '../../.env'),
        os.path.join(os.path.dirname(__file__), '../.env'),
    ]
    
    print("\nTrying possible .env paths:")
    # Try each possible path
    for env_file in potential_env_paths:
        print(f"Checking: {env_file}")
        print(f"File exists: {os.path.exists(env_file)}")
        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            print(f"Loaded .env from: {env_file}")
            break
    
    # Print environment variables (without sensitive data)
    print("\nEnvironment variables:")
    print(f"MODEL: {os.environ.get('MODEL')}")
    print(f"PROVIDER: {os.environ.get('PROVIDER')}")
    print(f"LOG_LEVEL: {os.environ.get('LOG_LEVEL')}")
    print(f"OPENAI_API_KEY exists: {bool(os.environ.get('OPENAI_API_KEY'))}")
    print("=== End Debug ===\n")
    
    return Settings() 