from functools import lru_cache

from app.core.config import get_settings
from app.storage.base import StorageBackend
from app.storage.local import LocalStorage


@lru_cache
def get_storage() -> StorageBackend:
    settings = get_settings()
    backend = settings.storage_backend
    if backend == "local":
        return LocalStorage(settings.local_storage_dir)
    if backend == "s3":
        # F-10 で boto3 ベースの S3Storage を実装予定
        raise NotImplementedError("S3 ストレージは F-10 で実装予定です")
    raise ValueError(f"未知の STORAGE_BACKEND: {backend}")
