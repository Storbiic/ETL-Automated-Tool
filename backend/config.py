"""
Configuration settings for the ETL backend
"""
import os
from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "ETL Automation Tool API"
    api_version: str = "2.0.0"
    api_description: str = "Backend API for ETL data processing and automation"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # File Upload Settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    allowed_extensions: list = [".csv", ".xls", ".xlsx"]
    
    # CORS Settings
    cors_origins: list = ["http://localhost:8501", "http://127.0.0.1:8501"]
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure upload directory exists
Path(settings.upload_dir).mkdir(exist_ok=True)
