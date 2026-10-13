"""
CRIMENET-X Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import shutil


def get_default_database_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    # When deployed to Vercel (read-only serverless environment),
    # use /tmp where SQLite has write permissions.
    if os.environ.get("VERCEL"):
        tmp_db = "/tmp/crimenet_x.db"
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        seed_db = os.path.join(base_dir, "crimenet_x.db")
        if os.path.exists(seed_db) and not os.path.exists(tmp_db):
            try:
                shutil.copyfile(seed_db, tmp_db)
            except Exception:
                pass
        return f"sqlite:///{tmp_db}"

    return "sqlite:///./crimenet_x.db"


class Settings(BaseSettings):
    APP_NAME: str = "CrimeNet-X"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Criminal Network Intelligence & Incident Analysis System"
    
    # Database
    DATABASE_URL: str = get_default_database_url()
    
    # API
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Demo Mode
    DEMO_INTERVAL_MIN: float = 2.0
    DEMO_INTERVAL_MAX: float = 4.0
    
    # Analytics
    PATTERN_THRESHOLD: int = 3
    HOTSPOT_HIGH_THRESHOLD: int = 15
    HOTSPOT_MEDIUM_THRESHOLD: int = 8
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
