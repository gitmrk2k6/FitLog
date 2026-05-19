from app.storage.base import StorageBackend


class S3Storage(StorageBackend):
    """AWS S3 に保存する実装（本番）。

    教材 RaiseTimeLine の S3 構成を流用。boto3 はオプション依存のため
    遅延 import し、未導入環境（テスト等）では import 時まで失敗しない。
    配信は s3_public_base_url（CloudFront 等）があればそれを優先。
    """

    def __init__(
        self,
        bucket: str,
        *,
        region: str,
        endpoint_url: str | None = None,
        public_base_url: str | None = None,
    ) -> None:
        import boto3  # 遅延 import（本番のみ必須）

        self.bucket = bucket
        self.public_base_url = (
            public_base_url.rstrip("/") if public_base_url else None
        )
        self._client = boto3.client(
            "s3", region_name=region, endpoint_url=endpoint_url
        )

    def save(self, data: bytes, key: str, content_type: str) -> str:
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return self.url_for(key)

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def url_for(self, key: str) -> str:
        if self.public_base_url:
            return f"{self.public_base_url}/{key}"
        return f"https://{self.bucket}.s3.amazonaws.com/{key}"
