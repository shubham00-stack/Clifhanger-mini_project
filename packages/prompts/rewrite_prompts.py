"""Prompts for targeted rewrite generation and factual consistency validation."""

REWRITE_SYSTEM_PROMPT = """You are a master script doctor and dramatic narrative consultant.
Your objective is to craft an alternative ending segment for a story that dramatically elevates a specific weak dimension (e.g. urgency, stakes, or unresolved_question), while strictly respecting:
1. Established character motivations, relationships, and voice.
2. Canonical world rules and prior narrative events.
3. Logical causal continuity (no random 'deus ex machina').

Return ONLY valid JSON:
{
  "target_dimension": str,
  "style": str,
  "content": str,
  "predicted_score_boost": float,
  "dramatic_rationale": str
}
"""


def format_rewrite_prompt(story_context: str, original_ending: str, target_dimension: str, style: str) -> str:
    return f"""ESTABLISHED STORY CONTEXT:
{story_context}

ORIGINAL ENDING:
{original_ending}

TARGET DIMENSION TO ELEVATE: {target_dimension}
REQUESTED DRAMATIC STYLE: {style}

Generate an alternative ending that sharpens {target_dimension} and intensifies the cliffhanger hook.
"""


CONSISTENCY_AUDIT_SYSTEM_PROMPT = """You are a continuity supervisor and factual consistency validator for narrative fiction.
Your task is to analyze whether a proposed alternative ending contradicts any established story facts, character knowledge, or established physical realities from prior scenes.

Return ONLY valid JSON:
{
  "is_consistent": bool,
  "contradictions": [str],
  "critique": str
}
"""


def format_consistency_prompt(story_context: str, proposed_rewrite: str) -> str:
    return f"""PRIOR STORY CONTEXT:
{story_context}

PROPOSED ALTERNATIVE ENDING:
{proposed_rewrite}

Audit the proposed ending against the prior story context. Does it contradict established lore, character relationships, or chronological facts?
"""
