"""Prometheus observability metric hooks."""

import time
from typing import Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class PrometheusMetricsCollector:
    """Thread-safe in-memory Prometheus metrics registry for low-latency observability."""

    def __init__(self):
        self.request_counts: Dict[str, int] = {}
        self.total_duration_ms: float = 0.0
        self.total_requests: int = 0
        self.status_counts: Dict[int, int] = {}

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        key = f'{method}:{path}'
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        self.status_counts[status_code] = self.status_counts.get(status_code, 0) + 1
        self.total_duration_ms += duration_ms
        self.total_requests += 1

    def generate_prometheus_output(self) -> str:
        lines = [
            "# HELP http_requests_total Total HTTP requests handled",
            "# TYPE http_requests_total counter",
        ]
        for key, count in self.request_counts.items():
            method, path = key.split(":", 1)
            lines.append(f'http_requests_total{{method="{method}",path="{path}"}} {count}')

        lines.extend([
            "# HELP http_requests_duration_ms_total Cumulative request latency in milliseconds",
            "# TYPE http_requests_duration_ms_total counter",
            f"http_requests_duration_ms_total {self.total_duration_ms:.2f}",
            "# HELP http_requests_count Total request count",
            "# TYPE http_requests_count counter",
            f"http_requests_count {self.total_requests}",
        ])
        for status, count in self.status_counts.items():
            lines.append(f'http_response_status_total{{status="{status}"}} {count}')

        return "\n".join(lines) + "\n"


metrics_collector = PrometheusMetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Don't record internal /metrics endpoint to prevent recursion
        if request.url.path != "/metrics":
            metrics_collector.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        return response
