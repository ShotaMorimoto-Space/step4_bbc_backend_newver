# app/core/config.py
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ===== App =====
    env: str = "development"
    log_level: str = "INFO"

    # ===== DB =====
    database_url: Optional[str] = None
    database_host: str = "localhost"
    database_port: int = 3306
    database_name: str = "test"
    database_username: str = "root"
    database_password: str = ""

    # ===== JWT / Auth =====
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ===== Azure Blob Storage =====
    azure_storage_connection_string: Optional[str] = None
    azure_video_container: Optional[str] = None
    azure_thumbnail_container: Optional[str] = None
    azure_section_image_container: Optional[str] = None
    azure_audio_container: Optional[str] = None
    public_cdn_base_url: Optional[str] = None

    # ===== OpenAI =====
    openai_api_key: Optional[str] = None

    # ===== LINE Messaging API =====
    line_channel_secret: Optional[str] = None
    line_channel_access_token: Optional[str] = None
    line_verify_signature: bool = True
    line_reply_enabled: bool = True

    # ===== CORS =====
    cors_allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,  # ★ 大文字・小文字の差を吸収する
        extra="ignore",
    )

    def assemble_db_url(self) -> str:
        """
        database_url があればそれを使う。
        無ければ分割値から DSN を構築。
        """
        if self.database_url:
            return self.database_url
        password = quote_plus(self.database_password or "")
        return (
            f"mysql+asyncmy://{self.database_username}:{password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
