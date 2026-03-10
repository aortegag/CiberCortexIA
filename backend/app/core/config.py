from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "CiberCortex IA"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DB_USER: str = "cybercortex"
    DB_PASSWORD: str = "cybercortex"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cybercortex"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-before-any-deployment"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS — comma-separated in env, parsed to list
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    AI_RATE_LIMIT_PER_USER_PER_HOUR: int = 5
    AI_CACHE_TTL_SECONDS: int = 86400  # 24h

    # NVD
    NVD_API_KEY: str = ""
    NVD_API_BASE_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    NVD_RATE_LIMIT_RPM: int = 5  # 5/min without key; 50/min with key

    # Reports
    REPORTS_DIR: str = "/tmp/cybercortex/reports"

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()
