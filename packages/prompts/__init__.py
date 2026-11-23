"""Versioned prompt templates for narrative analysis and rewrites."""

from .narrative_analysis import (
    PROMPT_VERSION,
    NARRATIVE_ANALYSIS_SYSTEM_PROMPT,
    format_narrative_prompt,
)
from .rewrite_prompts import (
    REWRITE_SYSTEM_PROMPT,
    format_rewrite_prompt,
    CONSISTENCY_AUDIT_SYSTEM_PROMPT,
    format_consistency_prompt,
)

__all__ = [
    "PROMPT_VERSION",
    "NARRATIVE_ANALYSIS_SYSTEM_PROMPT",
    "format_narrative_prompt",
    "REWRITE_SYSTEM_PROMPT",
    "format_rewrite_prompt",
    "CONSISTENCY_AUDIT_SYSTEM_PROMPT",
    "format_consistency_prompt",
]
