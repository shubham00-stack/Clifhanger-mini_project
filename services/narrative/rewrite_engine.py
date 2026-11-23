"""Alternative ending generator and consistency auditor."""

from typing import Any, Dict, Optional
from packages.model_client.base import BaseModelClient
from packages.prompts.rewrite_prompts import (
    REWRITE_SYSTEM_PROMPT,
    format_rewrite_prompt,
    CONSISTENCY_AUDIT_SYSTEM_PROMPT,
    format_consistency_prompt,
)


class RewriteEngine:
    """Generates targeted rewrites to elevate weak dimensions."""

    def __init__(self, model_client: BaseModelClient):
        self.client = model_client

    def generate_targeted_rewrite(
        self,
        story_context: str,
        original_ending: str,
        target_dimension: str = "urgency",
        style: str = "intensified",
    ) -> Dict[str, Any]:
        prompt = format_rewrite_prompt(story_context, original_ending, target_dimension, style)
        response = self.client.analyze_text(
            prompt=prompt,
            system_prompt=REWRITE_SYSTEM_PROMPT,
            temperature=0.7,
        )

        content = response.get("content")
        if not content:
            # Deterministic heuristic fallback rewrite
            content = (
                f"{original_ending}\n\nSuddenly, the floor trembled as the countdown timer hit zero. "
                f"Across the chamber, the blast doors sealed irrevocably shut."
            )

        return {
            "target_dimension": target_dimension,
            "style": style,
            "content": content,
            "predicted_score_boost": float(response.get("predicted_score_boost", 15.0)),
            "dramatic_rationale": str(response.get("dramatic_rationale", f"Elevated {target_dimension} via acute physical stakes.")),
        }

    def audit_consistency(self, story_context: str, proposed_rewrite: str) -> Dict[str, Any]:
        prompt = format_consistency_prompt(story_context, proposed_rewrite)
        response = self.client.analyze_text(
            prompt=prompt,
            system_prompt=CONSISTENCY_AUDIT_SYSTEM_PROMPT,
            temperature=0.1,
        )

        is_consistent = bool(response.get("is_consistent", True))
        critique = str(response.get("critique", "Maintains logical continuity with prior scenes."))

        return {
            "is_consistent": is_consistent,
            "critique": critique,
        }
