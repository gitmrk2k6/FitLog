from pathlib import Path

import pytest

from app.main import app
from app.storage.factory import get_storage
from app.storage.local import LocalStorage

# 1x1 透明 PNG（最小実体）
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000154a24f600000000049454e44ae42"
    "6082"
)
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 64 + b"\xff\xd9"


@pytest.fixture
def ex_ids(common_exercises):
    return [e.id for e in common_exercises]


@pytest.fixture
def storage_dir(tmp_path, client):
    """get_storage を一時ディレクトリの LocalStorage に差し替える。"""
    d = tmp_path / "uploads"
    app.dependency_overrides[get_storage] = lambda: LocalStorage(str(d))
    yield d
    app.dependency_overrides.pop(get_storage, None)


def _create_workout(client, headers, ex_id) -> int:
    res = client.post(
        "/workouts",
        headers=headers,
        json={
            "performed_on": "2026-05-18",
            "exercises": [
                {"exercise_id": ex_id, "sets": [{"weight_kg": 60, "reps": 10}]}
            ],
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


def _put(client, wid, headers, name, data, ctype):
    return client.put(
        f"/workouts/{wid}/photo",
        headers=headers,
        files={"file": (name, data, ctype)},
    )


def test_upload_requires_auth(client, auth_headers, ex_ids, storage_dir):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = client.put(
        f"/workouts/{wid}/photo",
        files={"file": ("a.png", PNG_BYTES, "image/png")},
    )
    assert res.status_code == 401


def test_upload_nonexistent_workout_404(
    client, auth_headers, storage_dir
):
    assert _put(
        client, 999999, auth_headers, "a.png", PNG_BYTES, "image/png"
    ).status_code == 404


def test_upload_not_owner_403(
    client, auth_headers, other_headers, ex_ids, storage_dir
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert _put(
        client, wid, other_headers, "a.png", PNG_BYTES, "image/png"
    ).status_code == 403


def test_upload_invalid_type_422(
    client, auth_headers, ex_ids, storage_dir
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert _put(
        client, wid, auth_headers, "a.txt", b"hello", "text/plain"
    ).status_code == 422


def test_upload_empty_422(client, auth_headers, ex_ids, storage_dir):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert _put(
        client, wid, auth_headers, "a.png", b"", "image/png"
    ).status_code == 422


def test_upload_too_large_422(
    client, auth_headers, ex_ids, storage_dir
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    big = b"\x00" * (5 * 1024 * 1024 + 1)
    assert _put(
        client, wid, auth_headers, "big.jpg", big, "image/jpeg"
    ).status_code == 422


@pytest.mark.parametrize(
    "name,data,ctype,ext",
    [
        ("a.png", PNG_BYTES, "image/png", ".png"),
        ("a.jpg", JPEG_BYTES, "image/jpeg", ".jpg"),
    ],
)
def test_upload_success_persists_file(
    client, auth_headers, ex_ids, storage_dir, name, data, ctype, ext
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = _put(client, wid, auth_headers, name, data, ctype)
    assert res.status_code == 200
    body = res.json()
    assert body["photo_url"].startswith("/uploads/workouts/")
    assert body["photo_url"].endswith(ext)
    # 実体がストレージに書かれている
    key = body["photo_url"].split("/uploads/", 1)[1]
    saved = Path(storage_dir) / key
    assert saved.exists()
    assert saved.read_bytes() == data
    # 詳細にも反映
    detail = client.get(f"/workouts/{wid}", headers=auth_headers).json()
    assert detail["photo_url"] == body["photo_url"]


def test_delete_photo_clears_url(
    client, auth_headers, ex_ids, storage_dir
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    _put(client, wid, auth_headers, "a.png", PNG_BYTES, "image/png")
    res = client.delete(f"/workouts/{wid}/photo", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["photo_url"] is None
    detail = client.get(f"/workouts/{wid}", headers=auth_headers).json()
    assert detail["photo_url"] is None
