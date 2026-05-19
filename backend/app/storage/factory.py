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
        from app.storage.s3 import S3Storage

        return S3Storage(
            settings.s3_bucket,
            region=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            public_base_url=settings.s3_public_base_url,
        )
    raise ValueError(f"未知の STORAGE_BACKEND: {backend}")
