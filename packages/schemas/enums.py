"""Enumeration definitions for Cliffhanger Strength Analyzer."""

from enum import Enum


class ScoreBand(str, Enum):
    """Deterministic score bands defined in production roadmap."""
    NO_MEANINGFUL = "No Meaningful Cliffhanger"   # 0 - 29
    WEAK = "Weak"                                 # 30 - 49
    MODERATE = "Moderate"                         # 50 - 64
    STRONG = "Strong"                             # 65 - 79
    VERY_STRONG = "Very Strong"                   # 80 - 89
    EXCEPTIONAL = "Exceptional"                   # 90 - 100


class CliffhangerType(str, Enum):
    """12 distinct multi-label taxonomy classifications."""
    THREAT = "threat"                 # Direct physical or imminent danger
    DECISION = "decision"             # Irrevocable choice forced upon character
    REVELATION = "revelation"         # Groundbreaking truth unveiled to audience/character
    IDENTITY = "identity"             # Shocking revelation of true identity or allegiance
    RELATIONSHIP = "relationship"     # Romantic or interpersonal rupture/confession
    MISSION = "mission"               # Abrupt shift, failure, or escalation in core objective
    MORAL = "moral"                   # Ethical dilemma testing core values
    REVERSAL = "reversal"             # Sudden inversion of power or circumstance
    COUNTDOWN = "countdown"           # Explicit temporal deadline
    MYSTERY = "mystery"               # Baffling phenomenon requiring explanation
    PARALLEL = "parallel"             # Cross-cutting cliffhangers across simultaneous storylines
    EXISTENTIAL = "existential"       # Cosmic, metaphysical, or reality-altering disruption


class AssetType(str, Enum):
    """Supported narrative content asset types."""
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    SCREENPLAY = "screenplay"
    TRANSCRIPT = "transcript"


class AnalysisStatus(str, Enum):
    """Status lifecycle of an analysis run."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LocationType(str, Enum):
    """Scene location classification."""
    INT = "INT"
    EXT = "EXT"
    OTHER = "OTHER"


class ConflictType(str, Enum):
    """Story conflict classification."""
    PHYSICAL = "physical"
    PSYCHOLOGICAL = "psychological"
    INTERPERSONAL = "interpersonal"
    SOCIETAL = "societal"
    EXISTENTIAL = "existential"


class QuestionStatus(str, Enum):
    """Status of open narrative questions."""
    OPEN = "open"
    PARTIALLY_ANSWERED = "partially_answered"
    RESOLVED = "resolved"


class EpistemicStatus(str, Enum):
    """Audience vs character knowledge status."""
    SHARED = "shared"
    DRAMATIC_IRONY = "dramatic_irony"
    MYSTERY = "mystery"


class EvidenceType(str, Enum):
    """Type of narrative evidence cited."""
    VERBATIM_QUOTE = "verbatim_quote"
    SCENE_REFERENCE = "scene_reference"
    DIALOGUE_EXCHANGE = "dialogue_exchange"
    ACTION_BEAT = "action_beat"
