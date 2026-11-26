"""Prompts for targeted rewrite generation and strict factual consistency validation."""

from typing import Any, Dict, Optional

REWRITE_SYSTEM_PROMPT = """You are a master script doctor, dramatic narrative consultant, and strict continuity supervisor.
Your objective is to craft an alternative ending segment for a story that dramatically elevates a specific weak dimension (such as urgency, stakes, unresolved_question, or information_gap), while strictly adhering to the following FACT PRESERVATION RULES:

1. PRESERVE ALL ESTABLISHED CHARACTERS: Only utilize characters already named or present in the source excerpt. Do NOT introduce new characters, mysterious callers, reinforcements, or unnamed intruders.
2. PRESERVE THE EXISTING LOCATION: Keep the scene strictly within the physical space already established. Do NOT invent new architecture, rooms, blast doors, bulkheads, or escape tunnels unless already explicitly in the source.
3. PRESERVE ESTABLISHED OBJECTS & TECHNOLOGY: Only utilize physical items, tools, documents, or machines already present in the excerpt. Do NOT introduce countdown timers, ticking bombs, unexpected weapons, alarms, or gadgets that were not established.
4. PRESERVE THE EXISTING TIMELINE & ENVIRONMENT: Do NOT invent ungrounded external events, environmental shifts (e.g. floor trembling, earthquakes, sudden fires, electrical blackouts), or arbitrary countdowns.
5. NO CONTRADICTIONS: Do not contradict established character relationships, backstory, physical laws, or previous actions.
6. SUSPENSE THROUGH DRAMATIC MASTERY: Heighten suspense and cliffhanger hook exclusively through:
   - Deepening psychological stakes and moral choices for the established characters.
   - Sudden realization or shocking reinterpretation of existing clues, words, or documents (information gaps).
   - High-tension character dialogue, withheld confessions, or interrupted speech cutting off at peak suspense.
   - Pacing of actions and character choices with the existing objects and surroundings.
7. PERSPECTIVE & TONE: Faithfully preserve the original narrative perspective (POV), voice, and tone.

Return ONLY a valid JSON object matching this schema:
{
  "target_dimension": str,
  "style": str,
  "content": str,
  "predicted_score_boost": float,
  "dramatic_rationale": str,
  "preserved_facts": {
    "characters": [str],
    "location": str,
    "objects_used": [str],
    "timeline": str
  },
  "suspense_mechanism": str,
  "has_unsupported_facts": bool,
  "unsupported_facts": [str]
}
"""


def format_rewrite_prompt(
    story_context: str,
    original_ending: str,
    target_dimension: str,
    style: str,
    correction_feedback: Optional[str] = None,
) -> str:
    feedback_section = ""
    if correction_feedback:
        feedback_section = f"""
CRITICAL CORRECTION REQUIRED FROM PREVIOUS ATTEMPT:
{correction_feedback}
Do NOT repeat the above errors. Stay strictly grounded in the established excerpt.
"""

    return f"""ESTABLISHED STORY EXCERPT:
\"\"\"
{story_context.strip()}
\"\"\"

ORIGINAL ENDING SEGMENT:
\"\"\"
{original_ending.strip()}
\"\"\"

TARGET DIMENSION TO ELEVATE: {target_dimension}
REQUESTED DRAMATIC STYLE: {style}
{feedback_section}
FACT-PRESERVATION DIRECTIVE:
1. Examine the established story excerpt above. Identify the exact characters, location, objects, and situation.
2. Craft an intensified alternative ending that boosts the '{target_dimension}' cliffhanger dimension.
3. STRICT NEGATIVE CONSTRAINTS:
   - Do NOT introduce any new characters.
   - Do NOT add countdown timers, floor tremors, blast doors, or sudden new physical hazards unless they were already explicitly present in the excerpt.
   - Do NOT contradict any established facts.
4. Heighten suspense solely through existing characters, existing dialogue, discovered implications, withheld information, or pivotal character decisions.
"""


CONSISTENCY_AUDIT_SYSTEM_PROMPT = """You are an exacting continuity supervisor and factual consistency validator for narrative fiction.
Your job is to audit a proposed alternative ending against the original story excerpt.

You must examine two categories of errors:
1. CONTRADICTIONS: Direct conflicts with established character identities, knowledge, location, or lore.
2. UNSUPPORTED ADDITIONS / HALLUCINATIONS:
   - Introduction of new characters not present in the excerpt.
   - Introduction of new physical objects or mechanisms (e.g. countdown timers, blast doors, weapons, bombs) not present in the excerpt.
   - Introduction of new external events, environmental changes, or sudden catastrophes (e.g. floor trembling, explosions, sirens, power failure) not justified by the excerpt.

CRITICAL RULE:
If ANY contradictions exist OR ANY unsupported entities/events were introduced, you MUST set "is_consistent" to false and list them under "unsupported_entities" and "contradictions".
Only set "is_consistent" to true if the alternative ending strictly preserves all established scene facts.

Return ONLY valid JSON matching this schema:
{
  "is_consistent": bool,
  "contradictions": [str],
  "unsupported_entities": [str],
  "critique": str
}
"""


def format_consistency_prompt(story_context: str, proposed_rewrite: str) -> str:
    return f"""ORIGINAL STORY EXCERPT:
\"\"\"
{story_context.strip()}
\"\"\"

PROPOSED ALTERNATIVE ENDING:
\"\"\"
{proposed_rewrite.strip()}
\"\"\"

AUDIT INSTRUCTIONS:
Audit the proposed ending against the original story excerpt.
1. Are all characters in the proposed ending already present in the original excerpt?
2. Is the physical location identical?
3. Were any new physical objects (e.g., countdown timers, blast doors, weapons) or environmental events (e.g., floor tremors, explosions) invented that do not appear in the original excerpt?
4. Are there any direct factual contradictions?

If any new elements or contradictions are found, mark is_consistent as false and list each unsupported element.
"""
