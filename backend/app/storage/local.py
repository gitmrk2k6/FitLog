from pathlib import Path

from app.storage.base import StorageBackend


class LocalStorage(StorageBackend):
    """ローカルファイルシステムに保存する実装（開発用）。

    本番では S3 実装に差し替える前提。
    """

    def __init__(self, base_dir: str, public_prefix: str = "/uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.public_prefix = public_prefix.rstrip("/")

    def _path(self, key: str) -> Path:
        return self.base_dir / key

    def save(self, data: bytes, key: str, content_type: str) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return self.url_for(key)

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def url_for(self, key: str) -> str:
        return f"{self.public_prefix}/{key}"
