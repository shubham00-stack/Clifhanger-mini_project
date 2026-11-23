"""Security middleware enforcing payload limits and safe request handling."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from packages.shared.config import get_settings


class SecurityLimitsMiddleware(BaseHTTPMiddleware):
    """Enforces maximum payload size limits to protect against DoS and memory exhaustion."""
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > settings.max_payload_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Payload Too Large",
                            "message": f"Request body ({length} bytes) exceeds maximum limit ({settings.max_payload_bytes} bytes)",
                        },
                    )
            except ValueError:
                pass

        return await call_next(request)
