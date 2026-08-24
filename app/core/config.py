from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    PROJECT_NAME: str
    ENVIRONMENT: str
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    CORS_ORIGINS: list[str]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()