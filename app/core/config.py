# app/core/config.py
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- DB: どちらかで設定可 ---
    # 直接URLを置く場合（任意・無ければ下の分割項目から生成）
    DATABASE_URL: Optional[str] = None

    # 分割指定（あなたの .env に合わせて既に定義済み）
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "test"
    DATABASE_USERNAME: str = "root"
    DATABASE_PASSWORD: str = ""

    # --- JWT ---
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Azure Blob ---
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: str = "bbc-test"

    # --- Misc ---
    FRONTEND_ORIGINS: str = "http://localhost:3000"
    ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    def assemble_db_url(self) -> str:
        """
        DATABASE_URL があればそれを使う。なければ分割値から async DSN を構築。
        例: mysql+asyncmy://user:pass@host:3306/db
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        password = quote_plus(self.DATABASE_PASSWORD or "")
        return (
            f"mysql+asyncmy://{self.DATABASE_USERNAME}:{password}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.FRONTEND_ORIGINS.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
