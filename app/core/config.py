from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """base config settings"""
    PROJECT_NAME: str = "Task Manager API"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "5e58166b8fe35ecbdc90f842ccd98f9d0a0d9c2a0bbe831745a947b1a7b233c2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    DATABASE_URL: str = "sqlite+aiosqlite:///./tasks.db"
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()