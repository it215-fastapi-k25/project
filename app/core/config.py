from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")
    
    PROJECT_NAME: str = "Research Group Management API" 
    ENVIRONMENT : str = "development"
    DATABASE_URL: str 
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"] 
    
@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 