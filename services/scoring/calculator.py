from __future__ import annotations
"""Deterministic Cliffhanger Score Calculation Engine & Score Band Mapper."""

import math
from typing import Any, Dict, List, Tuple, Union
from packages.schemas.dimensions import (
    DIMENSION_WEIGHTS,
    DIMENSION_DEFINITIONS,
    DimensionName,
    DimensionScoreBreakdown,
    DimensionScoreInput,
)
from packages.schemas.enums import ScoreBand
from packages.shared.logging import get_logger

logger = get_logger("scoring.calculator")


def _safe_float(val: Any, default: float = 50.0) -> float:
    """Safely parses float handling None, NaN, Infinity, and invalid string inputs."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def map_score_to_band(score: float) -> ScoreBand:
    """
    Maps a final calculated score (0-100) to its deterministic Score Band as specified in Section 5.2:
    - 0-29: No Meaningful Cliffhanger
    - 30-49: Weak
    - 50-64: Moderate
    - 65-79: Strong
    - 80-89: Very Strong
    - 90-100: Exceptional
    """
    rounded = round(score, 2)
    if rounded < 30.0:
        return ScoreBand.NO_MEANINGFUL
    elif rounded < 50.0:
        return ScoreBand.WEAK
    elif rounded < 65.0:
        return ScoreBand.MODERATE
    elif rounded < 80.0:
        return ScoreBand.STRONG
    elif rounded < 90.0:
        return ScoreBand.VERY_STRONG
    else:
        return ScoreBand.EXCEPTIONAL


def calculate_cliffhanger_score(
    dimension_scores: Dict[str, Union[DimensionScoreInput, Dict[str, Union[float, str]]]],
) -> Tuple[float, ScoreBand, List[DimensionScoreBreakdown]]:
    """
    Calculates deterministic weighted cliffhanger score:
    Final Score = sum(w_i * D_i) for i in 1..9
    Ensures bit-for-bit repeatability and validates input completeness.
    """
    total_weighted_score = 0.0
    breakdowns: List[DimensionScoreBreakdown] = []

    for dim_name, weight in DIMENSION_WEIGHTS.items():
        if dim_name not in dimension_scores:
            # Default to neutral 50.0 if omitted with explicit log warning
            logger.warning("Missing dimension %s; defaulting to 50.0", dim_name)
            raw_score = 50.0
            confidence = 0.5
            explanation = "Defaulted due to missing model rating"
            missing_info = "Dimension was not provided by evaluator"
        else:
            val = dimension_scores[dim_name]
            if isinstance(val, DimensionScoreInput):
                raw_score = _safe_float(val.score, 50.0)
                confidence = _safe_float(val.confidence, 1.0)
                explanation = val.explanation
                missing_info = val.missing_info
            elif isinstance(val, dict):
                raw_score = _safe_float(val.get("score"), 50.0)
                confidence = _safe_float(val.get("confidence"), 1.0)
                explanation = str(val.get("explanation", ""))
                missing_info = str(val.get("missing_info", ""))
            else:
                raw_score = _safe_float(val, 50.0)
                confidence = 1.0
                explanation = ""
                missing_info = ""

        # Bound score between 0.0 and 100.0
        clamped_score = max(0.0, min(100.0, raw_score))
        weighted_val = weight * clamped_score
        total_weighted_score += weighted_val

        breakdowns.append(
            DimensionScoreBreakdown(
                dimension_name=dim_name,
                score=round(clamped_score, 2),
                weight=weight,
                weighted_contribution=round(weighted_val, 2),
                confidence=round(confidence, 2),
                explanation=explanation,
                missing_info=missing_info,
            )
        )

    final_score = round(total_weighted_score, 2)
    score_band = map_score_to_band(final_score)

    return final_score, score_band, breakdowns
