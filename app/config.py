"""Application configuration management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    aws_default_profile: Optional[str] = None
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    
    # Database
    database_path: str = "./data/letters.db"
    
    # Application
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Scraping
    frbsf_base_url: str = "https://www.frbsf.org/research-and-insights/publications/economic-letter/"
    scrape_timeout: int = 30
    max_retries: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
