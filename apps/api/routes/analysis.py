"""Cliffhanger analysis execution API routes."""

from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from packages.model_client.nim_client import NimModelClient
from packages.prompts.narrative_analysis import (
    PROMPT_VERSION,
    NARRATIVE_ANALYSIS_SYSTEM_PROMPT,
    format_narrative_prompt,
)
from packages.schemas.requests import AnalysisRequest, AnalysisResponse
from packages.shared.logging import get_logger
from services.narrative.segmenter import NarrativeSegmenter
from services.ingestion.parser import ManuscriptParser
from services.scoring.calculator import calculate_cliffhanger_score
from services.scoring.taxonomy import calibrate_and_filter_taxonomy

logger = get_logger("api.analysis")
router = APIRouter(prefix="/api", tags=["Analysis"])

ANALYSES_STORE: Dict[UUID, AnalysisResponse] = {}
PROJECT_ASSETS_STORE: Dict[UUID, List[Dict[str, Any]]] = {}
PROJECT_SCENES_STORE: Dict[UUID, List[Dict[str, Any]]] = {}


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


@router.post("/projects/{project_id}/upload", status_code=201)
def upload_document(
    project_id: UUID,
    file: UploadFile = File(...),
):
    """Upload PDF, DOCX, or TXT file, parse text, and perform automatic scene segmentation."""
    parser = ManuscriptParser()
    content_bytes = file.file.read()
    parsed = parser.parse_file(file.filename or "document.txt", content_bytes)

    asset_id = uuid4()
    asset_record = {
        "asset_id": asset_id,
        "project_id": project_id,
        "original_filename": parsed["original_filename"],
        "asset_type": parsed["asset_type"],
        "char_count": parsed["char_count"],
        "word_count": parsed["word_count"],
        "page_count": parsed.get("page_count", 1),
        "raw_text": parsed["raw_text"],
    }
    if project_id not in PROJECT_ASSETS_STORE:
        PROJECT_ASSETS_STORE[project_id] = []
    PROJECT_ASSETS_STORE[project_id].append(asset_record)

    # Segment scenes with provenance
    segmenter = NarrativeSegmenter()
    scenes = segmenter.segment_scenes_with_provenance(parsed["raw_text"])
    PROJECT_SCENES_STORE[project_id] = scenes

    return {
        "asset_id": str(asset_id),
        "project_id": str(project_id),
        "filename": parsed["original_filename"],
        "asset_type": parsed["asset_type"],
        "word_count": parsed["word_count"],
        "page_count": parsed.get("page_count", 1),
        "scene_count": len(scenes),
    }


@router.get("/projects/{project_id}/scenes")
def get_project_scenes(project_id: UUID):
    """Retrieve segmented scenes with headings, location types, and ending flags."""
    if project_id not in PROJECT_SCENES_STORE:
        raise HTTPException(status_code=404, detail="No scenes found for project")
    return PROJECT_SCENES_STORE[project_id]


@router.post("/projects/{project_id}/boundary")
def set_ending_boundary(
    project_id: UUID,
    scene_index: int = Query(..., description="Scene index to mark as the cliffhanger cutoff segment"),
):
    """Manually assign ending boundary segment for analysis."""
    if project_id not in PROJECT_SCENES_STORE:
        raise HTTPException(status_code=404, detail="No scenes found for project")

    scenes = PROJECT_SCENES_STORE[project_id]
    segmenter = NarrativeSegmenter()
    updated = segmenter.set_ending_boundary(scenes, boundary_scene_index=scene_index)
    PROJECT_SCENES_STORE[project_id] = updated
    return updated


@router.post("/analyze/document", response_model=AnalysisResponse, status_code=201)
def upload_and_analyze_document(
    file: UploadFile = File(...),
    project_id: Optional[UUID] = None,
    genre: Optional[str] = Form("Thriller"),
):
    """Direct end-to-end document upload, segmentation, and cliffhanger evaluation."""
    target_project_id = project_id or uuid4()
    parser = ManuscriptParser()
    content_bytes = file.file.read()
    parsed = parser.parse_file(file.filename, content_bytes)

    segmenter = NarrativeSegmenter()
    scenes = segmenter.segment_scenes_with_provenance(parsed["raw_text"])
    PROJECT_SCENES_STORE[target_project_id] = scenes

    # Find ending segment
    ending_scene = next((s for s in scenes if s.get("is_ending_segment")), None)
    ending_text = ending_scene["content"] if ending_scene else segmenter.extract_ending_segment(parsed["raw_text"])

    payload = AnalysisRequest(
        text=parsed["raw_text"],
        model_name="nvidia/nemotron-3-nano-omni-30b-a3b-instruct",
    )
    return analyze_cliffhanger(project_id=target_project_id, payload=payload)
