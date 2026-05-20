"""JSON 構造化ログ設定。

全ログを NDJSON（1行 1JSON）で標準出力に書き出す。
Datadog Agent / Datadog Forwarder はこの形式をそのままインジェストできる。
連携時は dd.trace_id / dd.span_id を ddtrace.tracer.current_span() の実値に差し替える。
"""

import logging
import logging.config

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

_SERVICE = "fitlog-api"
_VERSION = "0.1.0"


class _DatadogJsonFormatter(jsonlogger.JsonFormatter):
    """標準フィールド + Datadog 必須フィールドを付加するフォーマッタ。"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._settings = get_settings()

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = _SERVICE
        log_record["env"] = self._settings.env
        log_record["version"] = _VERSION

        # Datadog 分散トレーシングフィールド（スタブ）
        # 実連携時: ddtrace.tracer.current_span() から取得する
        log_record.setdefault("dd.trace_id", "0")
        log_record.setdefault("dd.span_id", "0")
        log_record["dd.service"] = _SERVICE
        log_record["dd.env"] = self._settings.env
        log_record["dd.version"] = _VERSION

        # 重複キーの除去
        log_record.pop("color_message", None)


def setup_logging() -> None:
    """アプリ起動時に一度だけ呼ぶ。ログ設定を初期化する。"""
    settings = get_settings()

    formatter = _DatadogJsonFormatter(
        fmt="%(message)s %(levelname)s %(name)s",
        timestamp=True,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())

    # uvicorn / SQLAlchemy の過剰なログを抑制
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """名前付きロガーを返す。呼び出し元: `logger = get_logger(__name__)`"""
    return logging.getLogger(name)
