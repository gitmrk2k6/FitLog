"""S3Storage の単体テスト（boto3 未導入環境ではスキップ）。"""

import sys
import types
from unittest.mock import MagicMock

import pytest


def _install_fake_boto3(monkeypatch) -> MagicMock:
    """boto3 を最小スタブに差し替え、S3 クライアント呼び出しを検証する。"""
    client = MagicMock()
    fake = types.ModuleType("boto3")
    fake.client = MagicMock(return_value=client)
    monkeypatch.setitem(sys.modules, "boto3", fake)
    return client


def test_s3_save_delete_and_url(monkeypatch):
    client = _install_fake_boto3(monkeypatch)
    from app.storage.s3 import S3Storage

    s = S3Storage("my-bucket", region="ap-northeast-1")
    url = s.save(b"data", "workouts/1/x.png", "image/png")

    client.put_object.assert_called_once_with(
        Bucket="my-bucket",
        Key="workouts/1/x.png",
        Body=b"data",
        ContentType="image/png",
    )
    assert url == "https://my-bucket.s3.amazonaws.com/workouts/1/x.png"

    s.delete("workouts/1/x.png")
    client.delete_object.assert_called_once_with(
        Bucket="my-bucket", Key="workouts/1/x.png"
    )


def test_s3_public_base_url_takes_precedence(monkeypatch):
    _install_fake_boto3(monkeypatch)
    from app.storage.s3 import S3Storage

    s = S3Storage(
        "my-bucket",
        region="ap-northeast-1",
        public_base_url="https://cdn.example.com/",
    )
    assert s.url_for("k/v.jpg") == "https://cdn.example.com/k/v.jpg"
