"""リクエスト / レスポンスの構造化ログミドルウェア。

各リクエストに UUID v4 の request_id を付与し、
処理完了後に method / path / status_code / duration_ms / user_id を JSON ログで出力する。
"""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.logging import get_logger

logger = get_logger("fitlog.request")

_REQUEST_ID_HEADER = "X-Request-ID"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        status_code = 500
        exc_message: str | None = None

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            exc_message = str(exc)
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            user_id: int | None = getattr(request.state, "user_id", None)

            extra = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
            }
            if exc_message:
                extra["error"] = exc_message

            if status_code >= 500:
                logger.error("unhandled exception" if exc_message else "server error", extra=extra)
            elif status_code >= 400:
                logger.warning("client error", extra=extra)
            else:
                logger.info("request completed", extra=extra)

        response.headers[_REQUEST_ID_HEADER] = request_id
        return response
