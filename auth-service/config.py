import os
from pydantic import BaseSettings, SecretStr, AnyUrl
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: SecretStr = os.getenv("SECRET_KEY", "!CHANGE_IN_PROD!")
    DATABASE_URL: AnyUrl = os.getenv("DATABASE_URL", "sqlite:///./authwifi.db")
    SMS_API_KEY: SecretStr = os.getenv("SMS_API_KEY", "")
    HOTSPOT_SECRET: SecretStr = os.getenv("HOTSPOT_SECRET", "")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TOKEN_TTL: int = int(os.getenv("TOKEN_TTL", "300"))  # 5 минут

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
