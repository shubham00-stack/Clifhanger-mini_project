"""Request-ID correlation tracking middleware."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from packages.shared.logging import current_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Ensures every request has an X-Request-ID header, propagates it into logging context,
    and returns it on the HTTP response for distributed tracing.
    """
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = current_request_id.set(req_id)
        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            current_request_id.reset(token)
