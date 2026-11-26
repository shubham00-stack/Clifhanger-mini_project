"""Regression test suite for analysis synchronization and alternative-ending state isolation.

Verifies:
1. Every new analysis receives a unique analysis ID and preserves its own story excerpt.
2. An alternative ending generated for Story 1 (Arjun & Dr. Meera) is never leaked or bound to Story 2 (Riya & Aarav).
3. Starting a new analysis for Story 2 has an empty rewrite state (no stale alternatives).
4. Generating an alternative for Story 2 uses only Story 2 characters (Riya, Aarav, blue box).
5. Switching between analyses preserves each analysis's distinct results without crosstalk.
"""

from uuid import uuid4
import pytest

from packages.schemas.requests import AnalysisRequest, RewriteRequest
from apps.api.routes.analysis import analyze_cliffhanger, get_analysis
from apps.api.routes.rewrites import generate_rewrite, list_rewrites


STORY_1_THE_LAST_TRANSMISSION = (
    "Arjun sprinted through the damp corridors of the underground research facility, "
    "his biometric keycard held tight against his chest. Ahead, Door 17 loomed in reinforced titanium, "
    "its hydraulic status indicator glowing a steady amber. "
    "Inside the primary laboratory, Dr. Meera was desperately wiping the memory arrays. "
    "'The perimeter sensors are offline, Arjun!' she called out, her voice echoing off the stainless steel benches. "
    "Arjun slotted his card into the terminal beside Door 17. The screen flashed: "
    "'Access Denied: Subject Arjun already authenticated inside Chamber 4. Duplicate identity detected.'"
)

STORY_2_THE_317_AM_CALL = (
    "At 3:17 AM, the vintage rotary telephone beside the hospital bed began to ring. "
    "Riya reached for it, her fingers brushing against the tarnished blue box resting on the nightstand. "
    "Her brother Aarav stood by the window, staring down at the empty city streets in the rain. "
    "Between them, their mother lay motionless under the sterile fluorescent light, "
    "clutching a faded black-and-white hospital photograph from thirty years ago. "
    "'Don't answer it, Riya,' Aarav whispered, his voice cracking. 'The doctor said the memory restoration procedure "
    "would only trigger if someone was transmitting the recall frequency from outside.'"
)


def test_complete_two_story_synchronization_lifecycle():
    """
    Executes the exact multi-story sequence reported in the issue:
    1. Evaluate Story 1 (The Last Transmission - Arjun & Meera).
    2. Generate its alternative ending.
    3. Start a new analysis.
    4. Enter Story 2 (The 3:17 AM Call - Riya & Aarav).
    5. Evaluate Story 2 and verify score/state.
    6. Verify Story 2 has NO alternative ending yet (no Arjun, Meera, Door 17).
    7. Generate a new alternative for Story 2.
    8. Verify Story 2's alternative features Riya, Aarav, mother, or blue box.
    9. Switch between analyses and verify strict isolation.
    """
    proj_id = uuid4()

    # Step 1: Evaluate Story 1
    req1 = AnalysisRequest(text=STORY_1_THE_LAST_TRANSMISSION)
    res1 = analyze_cliffhanger(project_id=proj_id, payload=req1)

    assert res1.analysis_id is not None
    assert res1.story_text == STORY_1_THE_LAST_TRANSMISSION
    assert res1.final_score > 0.0

    # Step 2: Generate alternative ending for Story 1
    rw_req1 = RewriteRequest(
        analysis_id=res1.analysis_id,
        target_dimension="urgency",
        style="intensified",
        story_text=STORY_1_THE_LAST_TRANSMISSION,
    )
    rw1 = generate_rewrite(analysis_id=res1.analysis_id, payload=rw_req1)

    assert rw1.analysis_id == res1.analysis_id
    rw1_lower = rw1.content.lower()
    assert "arjun" in rw1_lower or "meera" in rw1_lower or "door 17" in rw1_lower
    assert "riya" not in rw1_lower
    assert "aarav" not in rw1_lower

    # Step 3 & 4: Start new analysis and enter Story 2
    req2 = AnalysisRequest(text=STORY_2_THE_317_AM_CALL)
    res2 = analyze_cliffhanger(project_id=proj_id, payload=req2)

    # Step 5: Verify unique analysis ID and distinct results
    assert res2.analysis_id != res1.analysis_id
    assert res2.story_text == STORY_2_THE_317_AM_CALL

    # Step 6: Verify Alternative Endings for Story 2 are initially empty (no Arjun, Meera, Door 17 leakage)
    existing_rw2 = list_rewrites(res2.analysis_id)
    assert len(existing_rw2) == 0, "Story 2 should have no alternative endings before generation!"

    # Step 7: Generate new alternative for Story 2
    rw_req2 = RewriteRequest(
        analysis_id=res2.analysis_id,
        target_dimension="urgency",
        style="intensified",
        story_text=STORY_2_THE_317_AM_CALL,
    )
    rw2 = generate_rewrite(analysis_id=res2.analysis_id, payload=rw_req2)

    # Step 8: Verify Story 2 alternative uses Riya, Aarav, blue box, and NO Story 1 facts
    assert rw2.analysis_id == res2.analysis_id
    rw2_lower = rw2.content.lower()
    assert "riya" in rw2_lower or "aarav" in rw2_lower or "blue box" in rw2_lower or "mother" in rw2_lower
    assert "arjun" not in rw2_lower, "Arjun leaked into Story 2 alternative ending!"
    assert "meera" not in rw2_lower, "Dr. Meera leaked into Story 2 alternative ending!"
    assert "door 17" not in rw2_lower, "Door 17 leaked into Story 2 alternative ending!"

    # Step 9 & 10: Switch between recent analyses and verify each retains its own results
    retrieved_analysis_1 = get_analysis(res1.analysis_id)
    assert retrieved_analysis_1.story_text == STORY_1_THE_LAST_TRANSMISSION
    rewrites_1 = list_rewrites(res1.analysis_id)
    assert len(rewrites_1) == 1
    assert rewrites_1[0].rewrite_id == rw1.rewrite_id
    assert "arjun" in rewrites_1[0].content.lower() or "door 17" in rewrites_1[0].content.lower()

    retrieved_analysis_2 = get_analysis(res2.analysis_id)
    assert retrieved_analysis_2.story_text == STORY_2_THE_317_AM_CALL
    rewrites_2 = list_rewrites(res2.analysis_id)
    assert len(rewrites_2) == 1
    assert rewrites_2[0].rewrite_id == rw2.rewrite_id
    assert "riya" in rewrites_2[0].content.lower() or "aarav" in rewrites_2[0].content.lower()
