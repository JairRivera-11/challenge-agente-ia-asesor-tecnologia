from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: str = ""
    tavily_api_key: str = ""
    model_name: str = "gemini-3.5-flash"
    allow_user_keys: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()