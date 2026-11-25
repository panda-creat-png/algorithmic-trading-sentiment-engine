import json
import logging
import secrets
from typing import List, Union, Any
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_logger = logging.getLogger("quantmind.config")

INSECURE_SECRET_KEYS = frozenset({
    "",
    "secret",
    "changeme",
    "default",
    "dev-secret",
    "quantmind-ai-super-secret-development-jwt-key-replace-in-production",
})
MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantMind AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def assemble_debug(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on", "debug")
        return bool(v)
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """Enforces strong JWT signing keys in production and safe ephemeral defaults in dev."""
        env = self.ENVIRONMENT.strip().lower()
        is_production = env in ("production", "prod")
        key = (self.SECRET_KEY or "").strip()

        is_insecure = (
            not key
            or key.lower() in INSECURE_SECRET_KEYS
            or "replace-in-production" in key.lower()
            or len(key) < MIN_SECRET_KEY_LENGTH
        )

        if is_production and is_insecure:
            raise ValueError(
                "Insecure or missing SECRET_KEY for production environment. "
                f"SECRET_KEY must be set to a cryptographically random value of at least "
                f"{MIN_SECRET_KEY_LENGTH} characters (not a default development placeholder). "
                'Generate one via: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )

        if not key:
            self.SECRET_KEY = secrets.token_urlsafe(48)
            _logger.warning(
                "SECRET_KEY is not set; generated an ephemeral random key for %s mode. "
                "Set SECRET_KEY in .env to persist sessions across restarts.",
                self.ENVIRONMENT,
            )
        elif is_insecure:
            _logger.warning(
                "Using a weak or default development SECRET_KEY in %s mode. "
                "Replace SECRET_KEY before deploying to production.",
                self.ENVIRONMENT,
            )
        else:
            self.SECRET_KEY = key

        return self
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./quantmind.db"
    POSTGRES_USER: str = "quantuser"
    POSTGRES_PASSWORD: str = "quantpass"
    POSTGRES_DB: str = "quantmind"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Providers
    ALPACA_API_KEY: str = ""
    ALPACA_SECRET_KEY: str = ""
    ALPACA_PAPER: bool = True
    NEWS_API_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "QuantMindAI/1.0"
    TWITTER_BEARER_TOKEN: str = ""

    # AI Sentiment
    FINBERT_MODEL_NAME: str = "ProsusAI/finbert"
    SENTIMENT_BATCH_SIZE: int = 32
    USE_GPU_IF_AVAILABLE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
