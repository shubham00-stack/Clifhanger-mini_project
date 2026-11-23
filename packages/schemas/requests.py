"""API and MCP request/response contract models."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from .dimensions import DimensionName, DimensionScoreBreakdown
from .enums import ScoreBand, CliffhangerType


class AnalysisRequest(BaseModel):
    """Payload to trigger a cliffhanger analysis."""
    text: Optional[str] = Field(None, description="Raw narrative text or chapter ending")
    asset_id: Optional[UUID] = Field(None, description="Existing content asset UUID")
    ending_scene_index: Optional[int] = Field(None, description="Explicit ending scene index")
    model_name: Optional[str] = Field(None, description="Override model client identifier")


class AnalysisResponse(BaseModel):
    """Complete analysis output structure."""
    analysis_id: UUID
    project_id: UUID
    asset_id: UUID
    final_score: float = Field(..., ge=0.0, le=100.0)
    score_band: ScoreBand
    dimension_breakdown: List[DimensionScoreBreakdown]
    taxonomy_classifications: List[Dict[str, Any]]
    evidence_quotes: List[Dict[str, Any]]
    open_questions: List[str] = Field(default_factory=list)
    model_name: str
    prompt_version: str = "v1.0.0"


class RewriteRequest(BaseModel):
    """Payload to request an alternative ending."""
    analysis_id: UUID
    target_dimension: DimensionName = Field("urgency", description="Dimension to elevate")
    style: str = Field("intensified", description="Dramatic style modifier")


class RewriteResponse(BaseModel):
    """Generated rewrite and factual consistency review."""
    rewrite_id: UUID
    analysis_id: UUID
    target_dimension: DimensionName
    original_score: float
    predicted_score: float
    score_delta: float
    content: str
    is_consistent: bool
    validation_critique: str


class BenchmarkEvaluationResult(BaseModel):
    """Results from evaluating a dataset suite."""
    dataset_name: str
    sample_count: int
    mean_absolute_error: float
    spearman_correlation: float
    citation_accuracy: float
    taxonomy_precision: float
    taxonomy_recall: float
    taxonomy_f1: float
    regression_passed: bool
    details: List[Dict[str, Any]]
