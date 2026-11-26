"""Groq OpenAI-compatible model client with resilience, JSON repair, and live check."""

import os
from typing import Any, Dict, List, Optional, Type
import httpx
from pydantic import BaseModel

from .base import BaseModelClient
from .mock import MockModelClient
from .json_repair import repair_json
from ..shared.config import get_settings
from ..shared.errors import ModelProviderError, RateLimitError
from ..shared.logging import get_logger

logger = get_logger("model_client.groq")


class GroqModelClient(BaseModelClient):
    """
    Groq Cloud client utilizing Groq's high-speed inference engine.
    Compatible with the OpenAI completions protocol.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.groq_api_key
        self.base_url = (base_url or settings.groq_base_url).rstrip("/")
        self.model = model or settings.groq_model
        self.max_retries = max_retries or settings.max_retries
        self.mock_client = MockModelClient()

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def test_connection(self) -> Dict[str, Any]:
        """
        Tests connection to Groq API.
        Returns detailed diagnostics dictionary.
        """
        if not self.api_key or self.api_key.startswith("gsk-test") or self.api_key == "gsk-your-key-here" or self.api_key.strip() == "":
            return {
                "connected": False,
                "status": "unconfigured",
                "message": "GROQ_API_KEY is not set or using placeholder.",
                "model": self.model,
            }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(f"{self.base_url}/models", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    model_ids = [m.get("id") for m in data.get("data", [])]
                    return {
                        "connected": True,
                        "status": "live",
                        "model": self.model,
                        "available_models_count": len(model_ids),
                        "model_available": self.model in model_ids,
                    }
                else:
                    return {
                        "connected": False,
                        "status": f"http_{res.status_code}",
                        "message": res.text,
                        "model": self.model,
                    }
        except Exception as exc:
            return {
                "connected": False,
                "status": "connection_error",
                "message": str(exc),
                "model": self.model,
            }

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """Sends prompt to Groq chat completions, falling back to mock analyze_text if key is unset or unavailable."""
        if not self.api_key or self.api_key.startswith("gsk-test") or self.api_key == "gsk-your-key-here" or os.getenv("TESTING") == "1":
            logger.info("Using mock client for Groq generation (no live API key / testing mode)")
            res = self.mock_client.analyze_text(prompt, system_prompt, temperature=temperature)
            return str(res)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                if res.status_code == 429:
                    raise RateLimitError("Groq rate limit exceeded (429)")
                if res.status_code != 200:
                    raise ModelProviderError(f"Groq API error ({res.status_code}): {res.text}")

                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning(f"Groq API request failed: {exc}. Falling back to mock client.")
            res = self.mock_client.analyze_text(prompt, system_prompt, temperature=temperature)
            return str(res)

    def analyze_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Analyzes text with optional JSON schema enforcement."""
        if not self.api_key or self.api_key == "gsk-your-key-here" or os.getenv("TESTING") == "1":
            return self.mock_client.analyze_text(prompt, system_prompt, schema, temperature)
        if schema:
            res = self.generate_structured(prompt, schema, system_prompt, temperature)
            return res.model_dump()
        raw = self.generate(prompt, system_prompt, temperature)
        return repair_json(raw)

    def analyze_multimodal(
        self,
        content_parts: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        return self.mock_client.analyze_multimodal(content_parts, system_prompt, schema)

    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        return self.mock_client.generate_embedding(texts)

    def rerank_evidence(self, query: str, candidates: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        return self.mock_client.rerank_evidence(query, candidates, top_k)

    def extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        return self.mock_client.extract_document_content(file_bytes, mime_type)
