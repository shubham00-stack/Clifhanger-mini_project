"""Health check and model readiness route."""

from fastapi import APIRouter
from packages.model_client.nim_client import NimModelClient
from packages.shared.config import get_settings

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def get_health():
    settings = get_settings()
    has_api_key = bool(settings.nvidia_api_key and settings.nvidia_api_key != "nvapi-your-key-here")

    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "models": {
            "primary": settings.model_primary_narrative,
            "fallback": settings.model_fast_text,
            "verified_upstream": [settings.model_primary_narrative, settings.model_fast_text],
        },
        "mode": "live_nim" if has_api_key else "mock_provider",
    }
