from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://axis:axis@localhost:5432/axis_db"
    database_url_sync: str = "postgresql://axis:axis@localhost:5432/axis_db"
    auto_create_tables: bool = True  # Local convenience; production runs migrations explicitly.

    # Auth
    secret_key: str = "change-me-in-production-use-strong-random-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"]

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Storage
    storage_endpoint: str = "http://localhost:9000"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin"
    storage_bucket: str = "axis-evidence"
    storage_region: str = "us-east-1"

    # Action due-date defaults (days)
    major_nc_due_days: int = 90
    minor_nc_due_days: int = 30
    observation_due_days: int = 60

    # AI report drafting (optional; reports work without it)
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4.5"
    openrouter_referer: str = "http://localhost:3000"

    # Lag monitoring thresholds (days without activity)
    lag_at_risk_days: int = 7
    lag_at_risk_threshold_pct: float = 0.5  # 50% of window elapsed

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
