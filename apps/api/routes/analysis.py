"""Cliffhanger analysis execution API routes."""

from typing import Dict
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from packages.model_client.nim_client import NimModelClient
from packages.prompts.narrative_analysis import (
    PROMPT_VERSION,
    NARRATIVE_ANALYSIS_SYSTEM_PROMPT,
    format_narrative_prompt,
)
from packages.schemas.requests import AnalysisRequest, AnalysisResponse
from packages.shared.logging import get_logger
from services.narrative.segmenter import NarrativeSegmenter
from services.scoring.calculator import calculate_cliffhanger_score
from services.scoring.taxonomy import calibrate_and_filter_taxonomy

logger = get_logger("api.analysis")
router = APIRouter(prefix="/api", tags=["Analysis"])

ANALYSES_STORE: Dict[UUID, AnalysisResponse] = {}


@router.post("/projects/{project_id}/analyze", response_model=AnalysisResponse, status_code=201)
def analyze_cliffhanger(project_id: UUID, payload: AnalysisRequest):
    story_text = payload.text
    if not story_text or not story_text.strip():
        raise HTTPException(status_code=400, detail="Missing required narrative text payload")

    segmenter = NarrativeSegmenter()
    ending_segment = segmenter.extract_ending_segment(story_text)

    # Initialize model client
    client = NimModelClient()
    prompt = format_narrative_prompt(story_text=story_text, ending_segment=ending_segment)

    logger.info("Executing narrative evaluation for project %s", project_id)
    analysis_dict = client.analyze_text(
        prompt=prompt,
        system_prompt=NARRATIVE_ANALYSIS_SYSTEM_PROMPT,
    )

    # Deterministic scoring
    dim_scores = analysis_dict.get("dimension_scores", {})
    final_score, score_band, breakdowns = calculate_cliffhanger_score(dim_scores)

    # Multi-label taxonomy calibration
    raw_taxonomy = analysis_dict.get("taxonomy_classifications", [])
    calibrated_taxonomy = calibrate_and_filter_taxonomy(raw_taxonomy)

    # Evidence quotes
    evidence_quotes = analysis_dict.get("evidence_quotes", [])
    open_questions = analysis_dict.get("open_questions", [])

    analysis_id = uuid4()
    asset_id = payload.asset_id or uuid4()

    response = AnalysisResponse(
        analysis_id=analysis_id,
        project_id=project_id,
        asset_id=asset_id,
        final_score=final_score,
        score_band=score_band,
        dimension_breakdown=breakdowns,
        taxonomy_classifications=calibrated_taxonomy,
        evidence_quotes=evidence_quotes,
        open_questions=open_questions,
        model_name=payload.model_name or client.primary_model,
        prompt_version=PROMPT_VERSION,
    )

    ANALYSES_STORE[analysis_id] = response
    return response


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: UUID):
    if analysis_id not in ANALYSES_STORE:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return ANALYSES_STORE[analysis_id]
