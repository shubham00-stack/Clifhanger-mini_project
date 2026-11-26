"""Regression test suite for strict story consistency in alternative endings.

Verifies that the alternative ending generator strictly preserves established facts
(characters, location, timeline, objects, and events) and elevates suspense without
introducing unsupported elements (e.g. countdown timers, blast doors, or trembling floors).
"""

import re
from uuid import uuid4
import pytest

from packages.schemas.requests import AnalysisRequest, RewriteRequest
from apps.api.routes.analysis import analyze_cliffhanger
from apps.api.routes.rewrites import generate_rewrite
from services.narrative.rewrite_engine import RewriteEngine
from packages.model_client.mock import MockModelClient


THE_LAST_TRANSMISSION_STORY = (
    "Specialist Thomas adjusted the gain on the shortwave transceiver at Outpost 7. "
    "Outside, the sub-zero Arctic wind battered the reinforced radio hut, but inside, "
    "the only sound was the low drone of vacuum tubes and the hiss of atmospheric static. "
    "Officer Lin sat across the steel desk, methodically updating the station logbook with her fountain pen. "
    "'Nothing on the northern sweep for thirty-six hours,' Lin said without looking up. "
    "Just as Thomas reached to power down the reel-to-reel magnetic tape recorder, "
    "the receiver needle jumped violently to maximum amplitude. A crackle of static parted, "
    "and a hollow voice echoed from the metal speaker: 'Outpost 7, acknowledge. We have breached the perimeter.'"
)

THE_LAST_TRANSMISSION_ENDING = (
    "the receiver needle jumped violently to maximum amplitude. A crackle of static parted, "
    "and a hollow voice echoed from the metal speaker: 'Outpost 7, acknowledge. We have breached the perimeter.'"
)

FORBIDDEN_UNGROUNDED_TERMS = [
    r"\bcountdown\b",
    r"\btimer\b",
    r"\bblast\s+doors?\b",
    r"\b(?:floor|ground)\s+trembled\b",
    r"\b(?:floor|ground)\s+shook\b",
    r"\b00:0[0-9]\b",
    r"\bt-minus\b",
    r"\bhydraulic\b",
    r"\bcrowbar\b",
]

ALLOWED_CHARACTERS = {"thomas", "lin", "officer", "specialist"}


def test_baseline_analysis_the_last_transmission():
    """Verify that The Last Transmission establishes baseline score and evidence."""
    proj_id = uuid4()
    req = AnalysisRequest(text=THE_LAST_TRANSMISSION_STORY)
    res = analyze_cliffhanger(project_id=proj_id, payload=req)

    assert res.final_score > 0.0
    assert len(res.dimension_breakdown) == 9
    assert res.story_text == THE_LAST_TRANSMISSION_STORY
    return res


@pytest.mark.parametrize(
    "dimension",
    [
        "urgency",
        "unresolved_question",
        "stakes",
        "information_gap",
        "character_consequence",
    ],
)
def test_five_alternative_endings_story_consistency(dimension: str):
    """
    Test at least five alternative endings for 'The Last Transmission' across 5 key dimensions.
    Verifies:
    1. Character consistency: No new characters introduced.
    2. Location consistency: Retains Outpost 7 / radio room.
    3. Timeline consistency: Direct causal sequence.
    4. Object consistency: No countdown timers, blast doors, or crowbars.
    5. Event consistency: No ungrounded earthquakes or tremors.
    6. Suspense improvement: Predicted score >= baseline and score delta >= 0.
    """
    proj_id = uuid4()
    analysis_req = AnalysisRequest(text=THE_LAST_TRANSMISSION_STORY)
    analysis_res = analyze_cliffhanger(project_id=proj_id, payload=analysis_req)

    rewrite_req = RewriteRequest(
        analysis_id=analysis_res.analysis_id,
        target_dimension=dimension,
        style="intensified",
        story_text=THE_LAST_TRANSMISSION_STORY,
    )
    rewrite_res = generate_rewrite(analysis_id=analysis_res.analysis_id, payload=rewrite_req)

    content = rewrite_res.content
    content_lower = content.lower()

    # 1. Verify Suspense Improvement
    assert rewrite_res.predicted_score >= analysis_res.final_score
    assert rewrite_res.score_delta >= 0.0

    # 2. Verify Strict Continuity Status
    assert rewrite_res.is_consistent is True, f"Failed consistency on {dimension}: {rewrite_res.validation_critique}"
    assert rewrite_res.is_rejected is False
    assert len(rewrite_res.unsupported_additions) == 0

    # 3. Object & Event Consistency: Verify NO forbidden ungrounded terms are in the generated text
    for forbidden in FORBIDDEN_UNGROUNDED_TERMS:
        match = re.search(forbidden, content_lower)
        assert match is None, (
            f"Alternative ending for {dimension} introduced ungrounded trope '{forbidden}':\n{content}"
        )

    # 4. Location Consistency: Must stay in Outpost / radio station context
    assert not any(loc in content_lower for loc in ["catwalk", "bistro", "neo-seoul", "subway", "cellar"])

    # 5. Character Consistency: Check that no other third-party character names appear
    disallowed_characters = ["elena", "marcus", "kira", "mercer", "claire", "aldous", "holloway"]
    for char in disallowed_characters:
        assert char not in content_lower, f"Introduced unestablished character '{char}' in {dimension} ending!"

    # 6. Structured Output Verification
    assert "characters" in rewrite_res.preserved_facts
    assert rewrite_res.suspense_mechanism is not None
    assert len(rewrite_res.suspense_mechanism) > 5


def test_hallucination_detection_and_rejection():
    """
    Directly tests that the consistency auditor detects and rejects hallucinations
    such as countdown timers, blast doors, and floor tremors when they are not in the story.
    """
    client = MockModelClient()
    engine = RewriteEngine(model_client=client)

    hallucinated_ending = (
        f"{THE_LAST_TRANSMISSION_ENDING}\n\n"
        "Suddenly, the floor trembled as the countdown timer hit zero. "
        "Across the chamber, the blast doors sealed irrevocably shut."
    )

    audit = engine.audit_consistency(
        story_context=THE_LAST_TRANSMISSION_STORY,
        proposed_rewrite=hallucinated_ending,
    )

    assert audit["is_consistent"] is False
    assert len(audit["unsupported_entities"]) > 0

    detected_tropes = [e.lower() for e in audit["unsupported_entities"]]
    assert any("countdown" in t for t in detected_tropes), f"Failed to detect countdown: {detected_tropes}"
    assert any("blast doors" in t for t in detected_tropes), f"Failed to detect blast doors: {detected_tropes}"
    assert any("trembl" in t or "shak" in t for t in detected_tropes), f"Failed to detect tremor: {detected_tropes}"
