"""Alternative ending rewrite and consistency review routes."""

from typing import Dict, List
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from packages.model_client.nim_client import NimModelClient
from packages.schemas.requests import RewriteRequest, RewriteResponse
from services.narrative.rewrite_engine import RewriteEngine
from .analysis import ANALYSES_STORE

router = APIRouter(prefix="/api/analyses", tags=["Rewrites"])

REWRITES_STORE: Dict[UUID, List[RewriteResponse]] = {}


@router.post("/{analysis_id}/rewrite", response_model=RewriteResponse, status_code=201)
def generate_rewrite(analysis_id: UUID, payload: RewriteRequest):
    if analysis_id not in ANALYSES_STORE:
        raise HTTPException(status_code=404, detail="Baseline analysis not found")

    baseline = ANALYSES_STORE[analysis_id]
    client = NimModelClient()
    engine = RewriteEngine(model_client=client)

    story_context = f"Project {baseline.project_id} narrative context with baseline score {baseline.final_score:.1f}"
    original_ending = baseline.evidence_quotes[0].get("quote", "Original ending sequence") if baseline.evidence_quotes else "Original ending sequence"

    generated = engine.generate_targeted_rewrite(
        story_context=story_context,
        original_ending=original_ending,
        target_dimension=payload.target_dimension,
        style=payload.style,
    )

    audit = engine.audit_consistency(story_context, generated["content"])

    boost = generated.get("predicted_score_boost", 12.0)
    predicted_score = min(100.0, baseline.final_score + boost)

    rewrite = RewriteResponse(
        rewrite_id=uuid4(),
        analysis_id=analysis_id,
        target_dimension=payload.target_dimension,
        original_score=baseline.final_score,
        predicted_score=round(predicted_score, 2),
        score_delta=round(predicted_score - baseline.final_score, 2),
        content=generated["content"],
        is_consistent=audit["is_consistent"],
        validation_critique=audit["critique"],
    )

    if analysis_id not in REWRITES_STORE:
        REWRITES_STORE[analysis_id] = []
    REWRITES_STORE[analysis_id].append(rewrite)

    return rewrite


@router.get("/{analysis_id}/rewrites", response_model=List[RewriteResponse])
def list_rewrites(analysis_id: UUID):
    return REWRITES_STORE.get(analysis_id, [])
