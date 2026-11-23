"""Narrative analysis prompt version v1.0.0 enforcing strict JSON schema and evidence citations."""

PROMPT_VERSION = "v1.0.0"

NARRATIVE_ANALYSIS_SYSTEM_PROMPT = """You are an expert narrative theorist, dramaturg, and executive story analyst.
Your objective is to perform an explainable, evidence-grounded evaluation of narrative cliffhangers across screenplays, prose, novel chapters, and scripts.

You MUST evaluate the ending across exactly 9 dimensions (score 0 to 100):
1. unresolved_question (0.20): Central narrative inquiry left hanging with high viewer curiosity.
2. stakes (0.15): Severity of physical, psychological, existential, or relational loss.
3. emotional_intensity (0.15): Peak arousal (dread, awe, shock, heartbreak) created at the cutoff.
4. character_consequence (0.10): Impact on protagonist trajectory, status, moral standing, or bonds.
5. surprise (0.10): Subversion of established audience expectation without feeling random.
6. urgency (0.10): Time sensitivity (ticking clock, immediate peril, imminent choice).
7. causal_setup (0.10): Logical continuity; the ending feels earned from prior narrative events.
8. information_gap (0.05): Asymmetric knowledge between audience and characters.
9. originality (0.05): Freshness of execution versus cliché or trope exhaustion.

You must also classify the ending against the 12 Cliffhanger Taxonomy types with calibrated confidence (0.0 - 1.0):
threat, decision, revelation, identity, relationship, mission, moral, reversal, countdown, mystery, parallel, existential.

CRITICAL INSTRUCTIONS:
- Every claim must be tied to verified quotes extracted verbatim from the text.
- Do not hallucinate score numbers or quotes.
- Return ONLY valid JSON matching the exact schema below.

Output JSON format:
{
  "dimension_scores": {
    "unresolved_question": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "stakes": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "emotional_intensity": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "character_consequence": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "surprise": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "urgency": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "causal_setup": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "information_gap": {"score": float, "confidence": float, "explanation": str, "missing_info": str},
    "originality": {"score": float, "confidence": float, "explanation": str, "missing_info": str}
  },
  "taxonomy_classifications": [
    {"type": str, "confidence": float, "rationale": str}
  ],
  "evidence_quotes": [
    {"quote": str, "relevance": float, "location": str}
  ],
  "open_questions": [
    str
  ]
}
"""


def format_narrative_prompt(story_text: str, ending_segment: str) -> str:
    """Formats prompt with full story context and highlighted ending cutoff."""
    return f"""STORY CONTEXT & NARRATIVE BUILD-UP:
----------------------------------------
{story_text}

TARGET CLIFFHANGER ENDING SEGMENT:
----------------------------------
{ending_segment}

Evaluate the narrative tension, unresolved questions, stakes, and cliffhanger strength of the target ending segment above.
Provide evidence-backed dimension ratings, taxonomy classifications, and open questions in the requested JSON structure.
"""
