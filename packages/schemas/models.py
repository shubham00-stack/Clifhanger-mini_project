"""Pydantic core domain models aligned with SQLAlchemy schema specifications."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from .enums import (
    ScoreBand,
    CliffhangerType,
    AssetType,
    AnalysisStatus,
    LocationType,
    ConflictType,
    QuestionStatus,
    EpistemicStatus,
    EvidenceType,
)
from .dimensions import DimensionName, DimensionScoreBreakdown


# 1. Projects
class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    genre: Optional[str] = "drama"
    target_audience: Optional[str] = "general"


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 2. Content Assets
class ContentAssetBase(BaseModel):
    project_id: UUID
    asset_type: AssetType = AssetType.TEXT
    original_filename: str
    storage_path: Optional[str] = None
    raw_text: str
    char_count: int = 0
    word_count: int = 0


class ContentAssetCreate(ContentAssetBase):
    pass


class ContentAssetRead(ContentAssetBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 3. Scenes
class SceneBase(BaseModel):
    asset_id: UUID
    scene_index: int = 0
    heading: str = "SCENE 1"
    content: str
    location_type: LocationType = LocationType.OTHER
    is_ending_segment: bool = False


class SceneCreate(SceneBase):
    pass


class SceneRead(SceneBase):
    id: UUID = Field(default_factory=uuid4)


# 4. Characters
class CharacterBase(BaseModel):
    project_id: UUID
    name: str
    role: str = "protagonist"
    first_scene_id: Optional[UUID] = None
    traits: List[str] = Field(default_factory=list)


class CharacterRead(CharacterBase):
    id: UUID = Field(default_factory=uuid4)


# 5. Story Events
class StoryEventBase(BaseModel):
    scene_id: UUID
    event_order: int = 0
    description: str
    participants: List[str] = Field(default_factory=list)
    conflict_type: ConflictType = ConflictType.INTERPERSONAL


class StoryEventRead(StoryEventBase):
    id: UUID = Field(default_factory=uuid4)


# 6. Open Questions
class OpenQuestionBase(BaseModel):
    project_id: UUID
    scene_introduced_id: Optional[UUID] = None
    question_text: str
    status: QuestionStatus = QuestionStatus.OPEN
    importance_rating: float = Field(default=0.8, ge=0.0, le=1.0)


class OpenQuestionRead(OpenQuestionBase):
    id: UUID = Field(default_factory=uuid4)


# 9. Evidence Items
class EvidenceItemBase(BaseModel):
    analysis_id: UUID
    dimension_score_id: Optional[UUID] = None
    evidence_type: EvidenceType = EvidenceType.VERBATIM_QUOTE
    location_reference: str = "ending"
    quote: str
    relevance_score: float = Field(default=0.9, ge=0.0, le=1.0)
    epistemic_status: EpistemicStatus = EpistemicStatus.SHARED


class EvidenceItemCreate(EvidenceItemBase):
    pass


class EvidenceItemRead(EvidenceItemBase):
    id: UUID = Field(default_factory=uuid4)


# 8. Dimension Scores
class DimensionScoreBase(BaseModel):
    analysis_id: UUID
    dimension_name: DimensionName
    score: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explanation: str = ""
    missing_info: str = ""


class DimensionScoreCreate(DimensionScoreBase):
    pass


class DimensionScoreRead(DimensionScoreBase):
    id: UUID = Field(default_factory=uuid4)


# 7. Analysis Runs
class AnalysisRunBase(BaseModel):
    project_id: UUID
    asset_id: UUID
    ending_scene_id: Optional[UUID] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    final_score: Optional[float] = None
    score_band: Optional[ScoreBand] = None
    model_name: str = "nvidia/nemotron-3-nano-omni-30b-a3b-instruct"
    prompt_version: str = "v1.0.0"
    raw_response: Optional[str] = None
    error_message: Optional[str] = None


class AnalysisRunCreate(AnalysisRunBase):
    pass


class AnalysisRunRead(AnalysisRunBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dimension_scores: List[DimensionScoreBreakdown] = Field(default_factory=list)
    taxonomy_labels: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_items: List[EvidenceItemRead] = Field(default_factory=list)


# 10. Rewrites
class RewriteBase(BaseModel):
    analysis_id: UUID
    target_dimension: DimensionName = "urgency"
    style: str = "intensified"
    content: str
    predicted_score: Optional[float] = None
    is_consistent: bool = True
    validation_critique: Optional[str] = None


class RewriteCreate(RewriteBase):
    pass


class RewriteRead(RewriteBase):
    id: UUID = Field(default_factory=uuid4)
