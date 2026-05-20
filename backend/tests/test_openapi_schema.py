"""OpenAPI スキーマの完全性を検証するスモークテスト。

全エンドポイントに summary が設定されているか確認する。
デコレータの記述ミスでスキーマ生成が壊れた場合も検出できる。
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def schema():
    client = TestClient(app)
    res = client.get("/openapi.json")
    assert res.status_code == 200
    return res.json()


def test_openapi_schema_is_valid(schema):
    assert "paths" in schema
    assert len(schema["paths"]) > 0


def test_all_endpoints_have_summary(schema):
    missing = []
    for path, methods in schema["paths"].items():
        for method, op in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                if "summary" not in op:
                    missing.append(f"{method.upper()} {path}")
    assert not missing, f"summary が未設定のエンドポイント:\n" + "\n".join(missing)


def test_app_has_description(schema):
    assert schema["info"].get("description"), "FastAPI アプリに description が設定されていない"


def test_tags_have_descriptions(schema):
    tags = {t["name"]: t for t in schema.get("tags", [])}
    for tag in ["auth", "workouts", "users", "goals", "dashboard"]:
        assert tag in tags, f"タグ '{tag}' が openapi_tags に未登録"
        assert tags[tag].get("description"), f"タグ '{tag}' に description が未設定"
