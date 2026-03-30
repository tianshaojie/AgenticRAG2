"""Request tracing middleware: injects request_id and trace_id into log context."""

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Attach request_id, trace_id to structlog context for every request.

    Also logs request start/end with method, path, status, and latency_ms.
    request_id is generated server-side; trace_id honours X-Trace-ID header
    (forwarded from upstream proxy / API gateway if present).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID", request_id)

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
        )

        start_ms = time.monotonic_ns() // 1_000_000

        logger.info("request.start")

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id

        latency_ms = (time.monotonic_ns() // 1_000_000) - start_ms
        logger.info(
            "request.end",
            status_code=response.status_code,
            latency_ms=latency_ms,
        )

        return response
