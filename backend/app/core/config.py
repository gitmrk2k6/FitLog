from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境変数 / .env から読み込むアプリ設定。"""

    database_url: str = "postgresql+psycopg://fitlog:fitlog@localhost:5432/fitlog"
    test_database_url: str = "postgresql+psycopg://fitlog:fitlog@localhost:5432/fitlog_test"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    storage_backend: str = "local"
    local_storage_dir: str = "./var/uploads"

    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """設定インスタンスをキャッシュして返す。テストでは cache_clear() で差し替える。"""
    return Settings()
