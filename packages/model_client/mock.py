"""Deterministic MockModelClient for testing and offline evaluation without external tokens."""

import hashlib
import re
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

from .base import BaseModelClient


class MockModelClient(BaseModelClient):
    """
    Deterministic mock provider that produces realistic, calibrated ratings
    and evidence citations based on narrative cues or explicit overrides.
    Enables fully reproducible unit, integration, and regression testing.
    """

    def __init__(self, override_payload: Optional[Dict[str, Any]] = None):
        self.override_payload = override_payload

    def analyze_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        if self.override_payload:
            return self.override_payload

        # Calibrate output deterministically based on text content keywords or target_level hint
        prompt_lower = prompt.lower()

        # Extract realistic quote from prompt text if available
        quote_sample = "Complete thermal purge initiated. T-minus ten seconds. Escape pods jettisoned."
        if "ending" in prompt_lower:
            parts = re.split(r"ending[:\s]+", prompt, flags=re.IGNORECASE)
            if len(parts) > 1:
                ending_part = parts[1].strip()
                sentences = [s.strip() for s in ending_part.replace("\n", " ").split(".") if len(s.strip()) > 10]
                if sentences:
                    quote_sample = sentences[0]
        elif "context:" in prompt_lower:
            sentences = [s.strip() for s in prompt.replace("\n", " ").split(".") if len(s.strip()) > 10]
            if sentences:
                quote_sample = sentences[-1]

        if "target_level: strong" in prompt_lower or "strong" in prompt_lower or "electrifying" in prompt_lower or "bomb" in prompt_lower or "timer" in prompt_lower or "revelation" in prompt_lower:
            # Strong cliffhanger pattern (Score ~ 75-88)
            return {
                "dimension_scores": {
                    "unresolved_question": {"score": 88.0, "confidence": 0.95, "explanation": "Urgent life-or-death question hanging."},
                    "stakes": {"score": 90.0, "confidence": 0.95, "explanation": "Catastrophic loss of life imminent."},
                    "emotional_intensity": {"score": 85.0, "confidence": 0.90, "explanation": "High adrenaline dread."},
                    "character_consequence": {"score": 80.0, "confidence": 0.85, "explanation": "Protagonist identity exposed."},
                    "surprise": {"score": 82.0, "confidence": 0.85, "explanation": "Unexpected breach of security."},
                    "urgency": {"score": 92.0, "confidence": 0.95, "explanation": "Detonation in 00:03 seconds."},
                    "causal_setup": {"score": 86.0, "confidence": 0.90, "explanation": "Direct consequence of previous infiltration."},
                    "information_gap": {"score": 75.0, "confidence": 0.80, "explanation": "Audience realizes the trap before hero."},
                    "originality": {"score": 78.0, "confidence": 0.80, "explanation": "Clever mechanical misdirection."},
                },
                "taxonomy_classifications": [
                    {"type": "threat", "confidence": 0.95, "rationale": "Active danger mechanism."},
                    {"type": "countdown", "confidence": 0.92, "rationale": "Urgent countdown."},
                    {"type": "decision", "confidence": 0.85, "rationale": "Forced critical choice."},
                ],
                "evidence_quotes": [
                    {"quote": quote_sample, "relevance": 0.98, "location": "ending"},
                ],
                "open_questions": [
                    "Will the protagonist survive the blast or trigger the blast doors?",
                    "Who rewired the fail-safe behind their back?",
                ],
            }

        elif "target_level: weak" in prompt_lower or "weak" in prompt_lower or "mundane" in prompt_lower or "tea" in prompt_lower or "slept" in prompt_lower or "ledger" in prompt_lower or "train" in prompt_lower:
            # Weak cliffhanger pattern (Score ~ 25-35)
            return {
                "dimension_scores": {
                    "unresolved_question": {"score": 28.0, "confidence": 0.85, "explanation": "Vague question about tomorrow's schedule."},
                    "stakes": {"score": 20.0, "confidence": 0.85, "explanation": "Minor inconvenience if plans change."},
                    "emotional_intensity": {"score": 22.0, "confidence": 0.80, "explanation": "Low arousal, calm setting."},
                    "character_consequence": {"score": 18.0, "confidence": 0.75, "explanation": "No material change to character arc."},
                    "surprise": {"score": 15.0, "confidence": 0.75, "explanation": "Predictable sequence of events."},
                    "urgency": {"score": 12.0, "confidence": 0.80, "explanation": "No pressing temporal demand."},
                    "causal_setup": {"score": 65.0, "confidence": 0.80, "explanation": "Logically connected but low energy."},
                    "information_gap": {"score": 15.0, "confidence": 0.70, "explanation": "No meaningful secret revealed."},
                    "originality": {"score": 22.0, "confidence": 0.75, "explanation": "Conventional domestic scene."},
                },
                "taxonomy_classifications": [
                    {"type": "relationship", "confidence": 0.50, "rationale": "Casual conversation over breakfast."},
                ],
                "evidence_quotes": [
                    {"quote": quote_sample, "relevance": 0.85, "location": "ending"},
                ],
                "open_questions": [
                    "Will the protagonist remember their umbrella tomorrow morning?",
                ],
            }

        else:
            # Moderate cliffhanger pattern (Score ~ 54-62)
            return {
                "dimension_scores": {
                    "unresolved_question": {"score": 65.0, "confidence": 0.85, "explanation": "Clear mystery surrounding the discovery."},
                    "stakes": {"score": 55.0, "confidence": 0.85, "explanation": "Reputational risk if discovered."},
                    "emotional_intensity": {"score": 58.0, "confidence": 0.80, "explanation": "Moderate nervous anticipation."},
                    "character_consequence": {"score": 56.0, "confidence": 0.80, "explanation": "Could change standing with peers."},
                    "surprise": {"score": 58.0, "confidence": 0.75, "explanation": "Expected discovery of a clue."},
                    "urgency": {"score": 54.0, "confidence": 0.80, "explanation": "Approaching deadline."},
                    "causal_setup": {"score": 65.0, "confidence": 0.85, "explanation": "Follows logically from searching the premises."},
                    "information_gap": {"score": 62.0, "confidence": 0.75, "explanation": "Audience knows someone is outside the door."},
                    "originality": {"score": 52.0, "confidence": 0.75, "explanation": "Classic investigative trope."},
                },
                "taxonomy_classifications": [
                    {"type": "mystery", "confidence": 0.80, "rationale": "Unmarked item discovered."},
                    {"type": "threat", "confidence": 0.55, "rationale": "Voices approaching in hallway."},
                ],
                "evidence_quotes": [
                    {"quote": quote_sample, "relevance": 0.92, "location": "ending"},
                ],
                "open_questions": [
                    "What document is hidden inside the locked drawer?",
                    "Will the investigator conceal themselves before the guard enters?",
                ],
            }

    def analyze_multimodal(
        self,
        content_parts: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        text_content = " ".join([p.get("text", "") for p in content_parts if isinstance(p, dict)])
        return self.analyze_text(prompt=text_content, system_prompt=system_prompt, schema=schema)

    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        # Deterministic 16-dimensional pseudo-embeddings via hashing
        embeddings = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vec = [(b / 255.0) * 2.0 - 1.0 for b in digest[:16]]
            embeddings.append(vec)
        return embeddings

    def rerank_evidence(self, query: str, candidates: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        # Sort candidates deterministically by length and keyword overlap
        query_words = set(query.lower().split())
        scored = []
        for cand in candidates:
            cand_words = set(cand.lower().split())
            overlap = len(query_words.intersection(cand_words))
            score = 0.5 + 0.1 * min(overlap, 5)
            scored.append({"text": cand, "relevance_score": score})
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_k]

    def extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="replace")
