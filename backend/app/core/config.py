import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "finguard-super-secret-production-key-change-in-prod-xyz987")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database URL: Supports PostgreSQL and SQLite fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finguard.db")
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]
    
    # Risk Threshold Bands (Configurable 0-100)
    RISK_LOW_MAX: int = 29
    RISK_MEDIUM_MAX: int = 59
    RISK_HIGH_MAX: int = 79
    # 80-100 is Critical
    
    ALERT_TRIGGER_THRESHOLD: int = 60  # Any transaction >= 60 triggers an automated Alert
    
    # Demo Seed Settings
    DEMO_ADMIN_EMAIL: str = os.getenv("DEMO_ADMIN_EMAIL", "admin@finguard.ai")
    DEMO_ADMIN_PASSWORD: str = os.getenv("DEMO_ADMIN_PASSWORD", "Admin@123456")
    DEMO_ANALYST_EMAIL: str = os.getenv("DEMO_ANALYST_EMAIL", "analyst@finguard.ai")
    DEMO_ANALYST_PASSWORD: str = os.getenv("DEMO_ANALYST_PASSWORD", "Analyst@123456")
    
    # ML Model directory
    MODEL_DIR: str = os.getenv("MODEL_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml_pipeline/models")))

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
