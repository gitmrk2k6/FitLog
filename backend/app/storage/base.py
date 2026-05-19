from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """画像ストレージの抽象インターフェース（F-10）。

    ローカル / S3 を差し替え可能にする。F-10 実装時にアップロード
    エンドポイントから利用する。
    """

    @abstractmethod
    def save(self, data: bytes, key: str, content_type: str) -> str:
        """data を key で保存し、参照用 URL を返す。"""

    @abstractmethod
    def delete(self, key: str) -> None:
        """key のオブジェクトを削除する。"""

    @abstractmethod
    def url_for(self, key: str) -> str:
        """key の参照用 URL を返す。"""
