"""BaseModelClient abstraction as specified in Section 4.1."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel


class BaseModelClient(ABC):
    """Abstract interface defining required model capabilities."""

    @abstractmethod
    def analyze_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Analyzes text prompt with optional JSON schema enforcement."""
        pass

    @abstractmethod
    def analyze_multimodal(
        self,
        content_parts: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        """Analyzes multimodal content (text + visual/storyboard attachments)."""
        pass

    @abstractmethod
    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for text snippets."""
        pass

    @abstractmethod
    def rerank_evidence(self, query: str, candidates: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Reranks candidate evidence quotes based on relevance to query."""
        pass

    @abstractmethod
    def extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        """Parses document bytes using OCR or structured parsing."""
        pass
