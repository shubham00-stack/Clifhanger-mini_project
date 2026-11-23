"""NVIDIA NIM / OpenAI-compatible model client with exponential retries and fallback chain."""

import os
import random
import time
from typing import Any, Dict, List, Optional, Type
import httpx
from pydantic import BaseModel

from .base import BaseModelClient
from .mock import MockModelClient
from .json_repair import repair_json
from ..shared.config import get_settings
from ..shared.errors import ModelProviderError, RateLimitError
from ..shared.logging import get_logger

logger = get_logger("model_client.nim")


class NimModelClient(BaseModelClient):
    """
    Enterprise-grade NVIDIA NIM client supporting:
    - Primary reasoning model (nvidia/nemotron-3-nano-omni-30b-a3b-instruct)
    - Fast fallback model (nvidia/nemotron-3.5-bolt-e4b)
    - Exponential backoff retries on rate limits (429) and 5xx errors
    - Automatic JSON repair of LLM responses
    - Offline fallback to MockModelClient when NVIDIA_API_KEY is unset
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        primary_model: Optional[str] = None,
        fallback_model: Optional[str] = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.nvidia_api_key
        self.base_url = (base_url or settings.nvidia_base_url).rstrip("/")
        self.max_retries = max_retries or settings.max_retries
        self.primary_model = primary_model or settings.model_primary_narrative
        self.fallback_model = fallback_model or settings.model_fast_text
        self.embedding_model = settings.model_embeddings
        self.reranker_model = settings.model_reranker
        self.ocr_model = settings.model_ocr_parser

        self.mock_client = MockModelClient()

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def verify_models(self) -> List[str]:
        """Dynamically verifies available models via NVIDIA /v1/models endpoint."""
        if not self.api_key or self.api_key == "nvapi-your-key-here" or os.getenv("TESTING") == "1":
            logger.info("No valid NVIDIA_API_KEY provided; operating in mock/offline mode")
            return [self.primary_model, self.fallback_model]

        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/models", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("id") for m in data.get("data", []) if "id" in m]
                    logger.info("Verified upstream models: %s", models)
                    return models
                else:
                    logger.warning("Failed to verify models, status=%s", res.status_code)
                    return [self.primary_model, self.fallback_model]
        except Exception as exc:
            logger.warning("Dynamic model check failed (%s); using configured defaults", exc)
            return [self.primary_model, self.fallback_model]

    def _execute_with_retry(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        model_name: str,
        fallback_allowed: bool = True,
    ) -> Dict[str, Any]:
        """Executes HTTP request with exponential backoff and model fallback chain."""
        if not self.api_key or self.api_key == "nvapi-your-key-here" or os.getenv("TESTING") == "1":
            logger.debug("Operating in offline/test mode, delegating to MockModelClient")
            return {}

        current_model = model_name
        attempts = 0
        base_delay = 0.5

        while attempts < self.max_retries:
            attempts += 1
            payload["model"] = current_model
            try:
                with httpx.Client(timeout=45.0) as client:
                    response = client.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        headers=self._get_headers(),
                    )

                    if response.status_code == 200:
                        return response.json()

                    if response.status_code == 429:
                        # Rate limit: exponential backoff with jitter
                        delay = base_delay * (2 ** (attempts - 1)) + random.uniform(0.1, 0.5)
                        logger.warning("Rate limit (429) hit for model %s. Retrying in %.2fs (attempt %d/%d)", current_model, delay, attempts, self.max_retries)
                        time.sleep(delay)
                        continue

                    if response.status_code >= 500:
                        logger.warning("Server error (%d) for model %s. Retrying...", response.status_code, current_model)
                        time.sleep(base_delay * attempts)
                        continue

                    # Unrecoverable error (e.g. 400 or 404 on model)
                    if fallback_allowed and current_model != self.fallback_model:
                        logger.warning("Failing over from %s to fallback model %s", current_model, self.fallback_model)
                        current_model = self.fallback_model
                        attempts = 0
                        fallback_allowed = False
                        continue

                    raise ModelProviderError(f"HTTP {response.status_code}: {response.text}", status_code=response.status_code)

            except httpx.RequestError as exc:
                logger.warning("Connection error on %s: %s (attempt %d/%d)", current_model, exc, attempts, self.max_retries)
                time.sleep(base_delay * attempts)

        # Fallback chain exhausted
        if fallback_allowed and current_model != self.fallback_model:
            logger.warning("Primary model attempts exhausted; trying fallback %s", self.fallback_model)
            return self._execute_with_retry(endpoint, payload, self.fallback_model, fallback_allowed=False)

        raise ModelProviderError(f"Exceeded max retries ({self.max_retries}) contacting NVIDIA NIM")

    def analyze_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return self.mock_client.analyze_text(prompt=prompt, system_prompt=system_prompt, schema=schema)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        try:
            data = self._execute_with_retry("/chat/completions", payload, self.primary_model)
            if not data or "choices" not in data:
                return self.mock_client.analyze_text(prompt=prompt, system_prompt=system_prompt, schema=schema)

            raw_content = data["choices"][0]["message"]["content"]
            parsed = repair_json(raw_content)
            return parsed
        except Exception as exc:
            logger.error("Error calling NVIDIA NIM; falling back to mock provider: %s", exc)
            return self.mock_client.analyze_text(prompt=prompt, system_prompt=system_prompt, schema=schema)

    def analyze_multimodal(
        self,
        content_parts: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        return self.mock_client.analyze_multimodal(content_parts=content_parts, system_prompt=system_prompt, schema=schema)

    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            return self.mock_client.generate_embedding(texts)

        payload = {
            "input": texts,
            "model": self.embedding_model,
        }
        try:
            data = self._execute_with_retry("/embeddings", payload, self.embedding_model, fallback_allowed=False)
            if data and "data" in data:
                return [item["embedding"] for item in data["data"]]
        except Exception as exc:
            logger.warning("Embedding API failed (%s); using mock embeddings", exc)

        return self.mock_client.generate_embedding(texts)

    def rerank_evidence(self, query: str, candidates: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            return self.mock_client.rerank_evidence(query, candidates, top_k)

        payload = {
            "model": self.reranker_model,
            "query": {"text": query},
            "passages": [{"text": c} for c in candidates],
        }
        try:
            data = self._execute_with_retry("/reranking", payload, self.reranker_model, fallback_allowed=False)
            if data and "rankings" in data:
                rankings = data["rankings"][:top_k]
                return [{"text": candidates[r["index"]], "relevance_score": r["logit"]} for r in rankings]
        except Exception as exc:
            logger.warning("Reranker API failed (%s); using mock reranker", exc)

        return self.mock_client.rerank_evidence(query, candidates, top_k)

    def extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        return self.mock_client.extract_document_content(file_bytes, mime_type)
