from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="sqlite:///./customer_info.db",
        description="SQLAlchemy URL (postgresql+psycopg://... or sqlite:///...)",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:6001,http://127.0.0.1:6001",
        description="Comma-separated browser origins for CORS",
    )
    app_env: str = Field(default="development", description="development | production")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if value.startswith("sqlite"):
            return value
        if value.startswith("postgresql+psycopg://"):
            return value
        if value.startswith("postgresql://") or value.startswith("postgres://"):
            raise ValueError(
                "Use postgresql+psycopg://... for PostgreSQL DATABASE_URL values."
            )
        raise ValueError(
            "DATABASE_URL must use sqlite:///... or postgresql+psycopg://..."
        )

    @property
    def cors_origin_list(self) -> list[str]:
        configured = [o.strip() for o in self.cors_origins.split(",") if o.strip()]

        # Keep local dev resilient when frontend port changes (e.g. 5173 -> 6001).
        if self.app_env != "production":
            local_defaults = [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:6001",
                "http://127.0.0.1:6001",
            ]
            for origin in local_defaults:
                if origin not in configured:
                    configured.append(origin)

        return configured

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
