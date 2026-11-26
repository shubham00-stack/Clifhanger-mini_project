"""Health check and model readiness route."""

from fastapi import APIRouter
from packages.model_client.nim_client import NimModelClient
from packages.model_client.groq_client import GroqModelClient
from packages.shared.config import get_settings

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def get_health():
    settings = get_settings()
    has_nvidia = bool(settings.nvidia_api_key and settings.nvidia_api_key != "nvapi-your-key-here")
    has_groq = bool(settings.groq_api_key and settings.groq_api_key != "gsk-your-key-here")

    active_provider = "live_groq" if has_groq else ("live_nim" if has_nvidia else "mock_provider")

    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "models": {
            "primary": settings.model_primary_narrative,
            "fallback": settings.model_fast_text,
            "groq_model": settings.groq_model,
            "verified_upstream": [settings.model_primary_narrative, settings.model_fast_text],
        },
        "mode": active_provider,
        "groq_configured": has_groq,
        "nvidia_configured": has_nvidia,
    }


@router.get("/health/groq")
def test_groq_health():
    """Explicitly test Groq connection and return real diagnostic status."""
    client = GroqModelClient()
    return client.test_connection()
