"""構造化ログ・リクエストログミドルウェアのテスト。"""

import json
import logging

import pytest
from fastapi.testclient import TestClient

from app.core.logging import get_logger, setup_logging
from app.main import app


class _CaptureHandler(logging.Handler):
    """ログレコードをリストに蓄積するハンドラ。"""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture()
def capture_handler() -> _CaptureHandler:
    handler = _CaptureHandler()
    root = logging.getLogger()
    prev_level = root.level
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    yield handler
    root.removeHandler(handler)
    root.setLevel(prev_level)


# ── ロガー取得 ──────────────────────────────────────────────────────────────

def test_get_logger_returns_logger_with_correct_name() -> None:
    logger = get_logger("fitlog.test")
    assert logger.name == "fitlog.test"


# ── setup_logging ───────────────────────────────────────────────────────────

def test_setup_logging_sets_handler(monkeypatch) -> None:
    """setup_logging 後、root logger に StreamHandler が設定される。"""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    setup_logging()
    root = logging.getLogger()
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)


def test_setup_logging_respects_log_level(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    from app.core.config import get_settings
    get_settings.cache_clear()
    setup_logging()
    assert logging.getLogger().level == logging.WARNING
    get_settings.cache_clear()


# ── JSON フォーマット ────────────────────────────────────────────────────────

def test_log_output_is_valid_json(capture_handler: _CaptureHandler) -> None:
    """ログ行が JSON としてパースできること。"""
    import io
    import logging
    from pythonjsonlogger import jsonlogger
    from app.core.logging import _DatadogJsonFormatter

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(_DatadogJsonFormatter(fmt="%(message)s %(levelname)s %(name)s"))

    logger = logging.getLogger("fitlog._json_test")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.info("hello")
    output = stream.getvalue().strip()
    parsed = json.loads(output)

    assert parsed["message"] == "hello"
    assert parsed["level"] == "INFO"
    assert "timestamp" in parsed
    assert "dd.service" in parsed
    assert "dd.trace_id" in parsed

    logger.removeHandler(handler)


def test_datadog_fields_present_in_log(capture_handler: _CaptureHandler) -> None:
    """dd.* フィールドがすべて含まれること。"""
    import io
    from pythonjsonlogger import jsonlogger
    from app.core.logging import _DatadogJsonFormatter

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(_DatadogJsonFormatter(fmt="%(message)s %(levelname)s %(name)s"))

    logger = logging.getLogger("fitlog._dd_test")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.warning("dd check")
    parsed = json.loads(stream.getvalue().strip())

    for field in ("dd.trace_id", "dd.span_id", "dd.service", "dd.env", "dd.version"):
        assert field in parsed, f"missing field: {field}"

    logger.removeHandler(handler)


# ── RequestLoggingMiddleware ─────────────────────────────────────────────────

@pytest.fixture()
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_request_id_header_returned(client: TestClient) -> None:
    """レスポンスに X-Request-ID ヘッダが付くこと。"""
    response = client.get("/health")
    assert "x-request-id" in response.headers
    # UUID v4 形式（8-4-4-4-12）
    req_id = response.headers["x-request-id"]
    parts = req_id.split("-")
    assert len(parts) == 5


def test_health_endpoint_returns_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_request_log_contains_required_fields(
    client: TestClient, capture_handler: _CaptureHandler
) -> None:
    """リクエストログに必須フィールドが含まれること。"""
    client.get("/health")

    request_logs = [
        r for r in capture_handler.records if r.name == "fitlog.request"
    ]
    assert request_logs, "fitlog.request ログが出力されていない"

    record = request_logs[-1]
    for field in ("request_id", "method", "path", "status_code", "duration_ms"):
        assert hasattr(record, field) or field in record.__dict__, (
            f"ログレコードに {field} がない"
        )


def test_4xx_logged_as_warning(client: TestClient, capture_handler: _CaptureHandler) -> None:
    """存在しないパスへのリクエストは WARNING レベルで記録される。"""
    client.get("/nonexistent-path-12345")

    warning_logs = [
        r for r in capture_handler.records
        if r.name == "fitlog.request" and r.levelno == logging.WARNING
    ]
    assert warning_logs, "4xx は WARNING で記録されるべき"
