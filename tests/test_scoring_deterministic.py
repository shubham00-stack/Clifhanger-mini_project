"""Unit tests for deterministic scoring arithmetic and score band mapping."""

import pytest
from packages.schemas.dimensions import DIMENSION_WEIGHTS
from packages.schemas.enums import ScoreBand
from services.scoring.calculator import calculate_cliffhanger_score, map_score_to_band


def test_dimension_weights_sum_to_unity():
    """Assertion that the 9 dimension weights sum to exactly 1.00."""
    total_weight = sum(DIMENSION_WEIGHTS.values())
    assert abs(total_weight - 1.00) < 1e-9, f"Weights sum to {total_weight}, expected 1.00"
    assert len(DIMENSION_WEIGHTS) == 9


def test_score_band_mappings():
    """Verify all 6 deterministic score bands mapped correctly."""
    assert map_score_to_band(0.0) == ScoreBand.NO_MEANINGFUL
    assert map_score_to_band(29.4) == ScoreBand.NO_MEANINGFUL
    assert map_score_to_band(30.0) == ScoreBand.WEAK
    assert map_score_to_band(49.9) == ScoreBand.WEAK
    assert map_score_to_band(50.0) == ScoreBand.MODERATE
    assert map_score_to_band(64.9) == ScoreBand.MODERATE
    assert map_score_to_band(65.0) == ScoreBand.STRONG
    assert map_score_to_band(79.9) == ScoreBand.STRONG
    assert map_score_to_band(80.0) == ScoreBand.VERY_STRONG
    assert map_score_to_band(89.9) == ScoreBand.VERY_STRONG
    assert map_score_to_band(90.0) == ScoreBand.EXCEPTIONAL
    assert map_score_to_band(100.0) == ScoreBand.EXCEPTIONAL


def test_bit_for_bit_deterministic_repeatability():
    """Identical inputs must produce bit-for-bit identical outputs across multiple runs."""
    sample_scores = {
        "unresolved_question": {"score": 85.0, "confidence": 0.9},
        "stakes": {"score": 90.0, "confidence": 0.95},
        "emotional_intensity": {"score": 88.0, "confidence": 0.9},
        "character_consequence": {"score": 80.0, "confidence": 0.85},
        "surprise": {"score": 75.0, "confidence": 0.8},
        "urgency": {"score": 92.0, "confidence": 0.95},
        "causal_setup": {"score": 84.0, "confidence": 0.9},
        "information_gap": {"score": 70.0, "confidence": 0.8},
        "originality": {"score": 78.0, "confidence": 0.85},
    }

    first_score, first_band, first_breakdowns = calculate_cliffhanger_score(sample_scores)
    for _ in range(10):
        score, band, breakdowns = calculate_cliffhanger_score(sample_scores)
        assert score == first_score
        assert band == first_band
        assert len(breakdowns) == len(first_breakdowns)
        for b1, b2 in zip(first_breakdowns, breakdowns):
            assert b1.score == b2.score
            assert b1.weighted_contribution == b2.weighted_contribution


def test_score_clamping():
    """Ensure out-of-bounds scores are strictly clamped to [0, 100]."""
    out_of_bounds = {dim: 150.0 for dim in DIMENSION_WEIGHTS}
    score, band, _ = calculate_cliffhanger_score(out_of_bounds)
    assert score == 100.0
    assert band == ScoreBand.EXCEPTIONAL

    negative_scores = {dim: -50.0 for dim in DIMENSION_WEIGHTS}
    score_neg, band_neg, _ = calculate_cliffhanger_score(negative_scores)
    assert score_neg == 0.0
    assert band_neg == ScoreBand.NO_MEANINGFUL
