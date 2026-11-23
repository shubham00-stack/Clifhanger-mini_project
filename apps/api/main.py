"""FastAPI application entrypoint for Cliffhanger Strength Analyzer."""

from contextlib import asynccontextmanager
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from packages.shared.config import get_settings
from packages.shared.logging import configure_logging, current_request_id, get_logger
from apps.api.middleware.metrics import metrics_collector
from apps.api.routes import health, projects, analysis, rewrites, benchmarks

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Cliffhanger Strength Analyzer API initialized in %s mode on %s:%d", settings.app_env, settings.app_host, settings.app_port)
    yield


app = FastAPI(
    title="Cliffhanger Strength Analyzer API",
    description="Enterprise-grade explainable AI platform to evaluate narrative tension, stakes, and cliffhangers across screenplays and stories.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 1. CORS security restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# 2. Combined Observability, Tracing & Security Middleware
@app.middleware("http")
async def enterprise_pipeline_middleware(request: Request, call_next):
    # Enforce maximum payload size limit
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.max_payload_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Payload Too Large",
                        "message": f"Request body exceeds maximum allowed limit of {settings.max_payload_bytes} bytes",
                    },
                )
        except ValueError:
            pass

    # Request-ID tracking
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = current_request_id.set(req_id)

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Inject tracing header
        response.headers["X-Request-ID"] = req_id

        # Prometheus metrics recording
        if request.url.path != "/metrics":
            metrics_collector.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        return response
    finally:
        current_request_id.reset(token)


# 3. Mount API routers
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(analysis.router)
app.include_router(rewrites.router)
app.include_router(benchmarks.router)


# 4. Prometheus observability endpoint
@app.get("/metrics", response_class=PlainTextResponse, tags=["Observability"])
def get_metrics():
    """Exposes Prometheus scrape metrics."""
    return metrics_collector.generate_prometheus_output()
