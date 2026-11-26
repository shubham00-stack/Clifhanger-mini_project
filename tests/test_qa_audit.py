"""Comprehensive QA test suite testing the 8 key functional areas of Cliffhanger application."""

import os
from uuid import uuid4
import pytest

from packages.schemas.requests import AnalysisRequest, RewriteRequest
from apps.api.routes.analysis import analyze_cliffhanger, get_analysis
from apps.api.routes.rewrites import generate_rewrite, list_rewrites
from packages.model_client.mock import MockModelClient
from packages.model_client.groq_client import GroqModelClient
from packages.shared.config import get_settings
from services.scoring.calculator import calculate_cliffhanger_score, DIMENSION_WEIGHTS
from services.narrative.rewrite_engine import RewriteEngine


# AREA 1 & 2: Character/Fact Preservation & Contradiction Avoidance in Alternative Endings
def test_area1_and_2_story_consistency_and_contradiction_avoidance():
    engine = RewriteEngine(model_client=MockModelClient())
    original = (
        "Arjun stared at the illuminated panel of Door 17 in the subterranean laboratory. "
        "Dr. Meera checked her watch as the biometric scanner flashed yellow."
    )
    result = engine.generate_targeted_rewrite(
        story_context=original,
        original_ending="Dr. Meera checked her watch as the biometric scanner flashed yellow.",
        target_dimension="urgency",
    )
    assert result["is_consistent"] is True
    assert "Door 17" in result["content"] or "Arjun" in result["content"]
    assert result["predicted_score_boost"] > 0
    # Ensure no contradictory or ungrounded artifacts slipped past validation
    lowered = result["content"].lower()
    for forbidden in ["countdown timer", "floor trembling", "blast doors", "helicopter"]:
        assert forbidden not in lowered, f"Found forbidden hallucination: {forbidden}"


# AREA 3: Fact-Preserved indicator is calculated, not hardcoded
def test_area3_fact_preserved_indicator_calculation():
    engine = RewriteEngine(model_client=MockModelClient())
    original = "Arjun and Dr. Meera waited outside Door 17."
    
    # 1. Consistent alternative
    res_consistent = engine.generate_targeted_rewrite(
        story_context=original,
        original_ending=original,
        target_dimension="stakes",
    )
    assert isinstance(res_consistent["is_consistent"], bool)
    assert res_consistent["is_consistent"] is True
    
    # 2. Simulated hallucinated alternative audited directly
    contradictory_candidate = "Arjun sprinted through the blast doors as a countdown timer hit 00:05 and the floor began trembling."
    audit = engine.audit_consistency(original, contradictory_candidate)
    assert audit["is_consistent"] is False
    assert any(term in audit["critique"].lower() for term in ["blast doors", "countdown timer", "floor trembling", "unsupported", "consistency violation"])


# AREA 4: Tension Boost calculation is correct
def test_area4_tension_boost_calculation():
    project_id = uuid4()
    req = AnalysisRequest(text="Arjun stood before Door 17 in the vault with Dr. Meera.")
    analysis = analyze_cliffhanger(project_id=project_id, payload=req)
    baseline_score = analysis.final_score

    rw_req = RewriteRequest(
        analysis_id=analysis.analysis_id,
        target_dimension="urgency",
        style="intensified",
        story_text=req.text
    )
    rw = generate_rewrite(analysis_id=analysis.analysis_id, payload=rw_req)

    # Check arithmetic: predicted_score = min(100.0, baseline + boost) and score_delta = predicted_score - baseline
    expected_delta = round(rw.predicted_score - baseline_score, 2)
    assert abs(rw.score_delta - expected_delta) < 1e-4
    assert rw.predicted_score <= 100.0
    assert rw.predicted_score >= baseline_score


# AREA 5: Nine-dimensional score matches configured weighted formula
def test_area5_nine_dimensional_score_formula_weights():
    weights = DIMENSION_WEIGHTS
    assert len(weights) == 9
    assert round(sum(weights.values()), 6) == 1.000000

    dimension_scores = {
        "unresolved_question": 80.0,
        "stakes": 70.0,
        "emotional_intensity": 60.0,
        "character_consequence": 50.0,
        "surprise": 90.0,
        "urgency": 85.0,
        "causal_setup": 75.0,
        "information_gap": 65.0,
        "originality": 95.0,
    }

    expected_weighted_sum = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)
    actual_score, band, breakdowns = calculate_cliffhanger_score(dimension_scores)

    assert round(actual_score, 1) == round(expected_weighted_sum, 1)


# AREA 6: Groq API Client and connection diagnostic
def test_area6_groq_api_client():
    groq_client = GroqModelClient(api_key="gsk-test-key-mock")
    assert groq_client.model == "llama-3.3-70b-versatile"
    # When api_key is mock or in testing mode, generate() works gracefully via mock fallback
    response = groq_client.generate("Test prompt")
    assert isinstance(response, str)
    assert len(response) > 0

    # Test the connection diagnostic handler
    conn_info = groq_client.test_connection()
    assert "connected" in conn_info
    assert "status" in conn_info


# AREA 7: Report export format & content completeness
def test_area7_report_export_api_readiness():
    project_id = uuid4()
    story_payload = AnalysisRequest(
        text="Arjun and Dr. Meera stood before Door 17 in the underground vault.",
        target_audience="general",
        genre="sci-fi"
    )
    analysis = analyze_cliffhanger(project_id=project_id, payload=story_payload)
    analysis_id = analysis.analysis_id

    # Verify all components required for full report export exist
    assert analysis.final_score > 0
    assert analysis.score_band is not None
    assert len(analysis.dimension_breakdown) == 9
    assert analysis.evidence_quotes is not None

    # Generate rewrite
    rw_req = RewriteRequest(
        analysis_id=analysis_id,
        target_dimension="urgency",
        style="intensified",
        story_text=story_payload.text
    )
    rw = generate_rewrite(analysis_id=analysis_id, payload=rw_req)
    assert rw.analysis_id == analysis_id
    assert rw.is_consistent is True
    assert rw.score_delta > 0
    assert rw.content is not None


# AREA 8: Multiple analyses and switching without crosstalk
def test_area8_multiple_analyses_isolation():
    proj1 = uuid4()
    proj2 = uuid4()
    story1 = AnalysisRequest(text="Arjun and Dr. Meera unlocked Door 17 in the laboratory.")
    story2 = AnalysisRequest(text="Riya opened the blue box with Aarav in the hospital room.")

    res1 = analyze_cliffhanger(project_id=proj1, payload=story1)
    res2 = analyze_cliffhanger(project_id=proj2, payload=story2)

    id1 = res1.analysis_id
    id2 = res2.analysis_id

    assert id1 != id2

    # Fetch both individually
    get1 = get_analysis(id1)
    get2 = get_analysis(id2)

    assert get1.analysis_id == id1
    assert get2.analysis_id == id2
    assert "Door 17" in get1.story_text or "Arjun" in get1.story_text
    assert "blue box" in get2.story_text or "Riya" in get2.story_text

