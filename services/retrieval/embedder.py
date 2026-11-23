"""Vector retrieval and evidence reranking."""

import math
from typing import Any, Dict, List
from packages.model_client.base import BaseModelClient


class EvidenceRetriever:
    """Provides semantic search and reranking for narrative evidence quotes."""

    def __init__(self, model_client: BaseModelClient):
        self.client = model_client

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot / (norm1 * norm2)

    def retrieve_relevant_quotes(
        self,
        query: str,
        passages: List[str],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        if not passages:
            return []

        # Use reranker directly
        ranked = self.client.rerank_evidence(query, passages, top_k=top_k)
        return ranked
