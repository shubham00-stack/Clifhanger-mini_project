"""Cliffhanger scoring dimensions, weights, and definitions."""

from typing import Dict, Literal
from pydantic import BaseModel, Field

DimensionName = Literal[
    "unresolved_question",
    "stakes",
    "emotional_intensity",
    "character_consequence",
    "surprise",
    "urgency",
    "causal_setup",
    "information_gap",
    "originality",
]

# Exact weights defined in Section 5.1 (sum = 1.00)
DIMENSION_WEIGHTS: Dict[DimensionName, float] = {
    "unresolved_question": 0.20,
    "stakes": 0.15,
    "emotional_intensity": 0.15,
    "character_consequence": 0.10,
    "surprise": 0.10,
    "urgency": 0.10,
    "causal_setup": 0.10,
    "information_gap": 0.05,
    "originality": 0.05,
}

DIMENSION_DEFINITIONS: Dict[DimensionName, str] = {
    "unresolved_question": "Central narrative inquiry left hanging with high viewer curiosity.",
    "stakes": "Severity of physical, psychological, existential, or relational loss.",
    "emotional_intensity": "Peak arousal (dread, awe, shock, heartbreak) created at the cutoff.",
    "character_consequence": "Impact on protagonist trajectory, status, moral standing, or bonds.",
    "surprise": "Subversion of established audience expectation without feeling random.",
    "urgency": "Time sensitivity (ticking clock, immediate peril, imminent choice).",
    "causal_setup": "Logical continuity; the ending feels earned from prior narrative events.",
    "information_gap": "Asymmetric knowledge between audience and characters.",
    "originality": "Freshness of execution versus cliché or trope exhaustion.",
}


class DimensionScoreInput(BaseModel):
    """Raw score input for a single dimension."""
    score: float = Field(..., ge=0.0, le=100.0, description="Calibrated score from 0 to 100")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Model confidence from 0.0 to 1.0")
    explanation: str = Field(default="", description="Justification tied to narrative evidence")
    missing_info: str = Field(default="", description="Information that would raise the rating")


class DimensionScoreBreakdown(BaseModel):
    """Calculated breakdown of a scored dimension including weight and contribution."""
    dimension_name: DimensionName
    score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_contribution: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explanation: str = ""
    missing_info: str = ""
