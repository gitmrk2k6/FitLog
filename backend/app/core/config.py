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

    # F-10 S3（教材 RaiseTimeLine の構成を流用。storage_backend=s3 時に使用）
    s3_bucket: str = "fitlog-photos"
    s3_region: str = "ap-northeast-1"
    s3_endpoint_url: str | None = None  # MinIO/LocalStack 等テスト用
    s3_public_base_url: str | None = None  # CloudFront 等の配信ドメイン

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
