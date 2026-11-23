"""FastAPI route handler and API contracts integration tests."""

import pytest
from uuid import uuid4
from apps.api.main import app
from apps.api.routes.health import get_health
from apps.api.routes.projects import create_project, get_project, list_projects
from apps.api.routes.analysis import analyze_cliffhanger, get_analysis
from apps.api.routes.rewrites import generate_rewrite, list_rewrites
from apps.api.routes.benchmarks import run_benchmarks
from apps.api.middleware.metrics import metrics_collector
from packages.schemas.models import ProjectCreate
from packages.schemas.requests import AnalysisRequest, RewriteRequest


def test_openapi_schema_generation():
    """Verify OpenAPI schema generates cleanly with all routes and tags."""
    openapi = app.openapi()
    assert openapi["info"]["title"] == "Cliffhanger Strength Analyzer API"
    assert "/api/health" in openapi["paths"]
    assert "/api/projects" in openapi["paths"]
    assert "/api/projects/{project_id}/analyze" in openapi["paths"]
    assert "/api/analyses/{analysis_id}/rewrite" in openapi["paths"]
    assert "/api/benchmarks/run" in openapi["paths"]
    assert "/metrics" in openapi["paths"]


def test_health_route():
    health = get_health()
    assert health["status"] == "healthy"
    assert "models" in health
    assert "primary" in health["models"]


def test_prometheus_metrics_generation():
    metrics_collector.record_request("GET", "/api/health", 200, 1.25)
    output = metrics_collector.generate_prometheus_output()
    assert "http_requests_total" in output
    assert "http_requests_duration_ms_total" in output


def test_project_crud_lifecycle():
    proj_in = ProjectCreate(
        title="Operation Borealis",
        description="High arctic thriller",
        genre="thriller",
        target_audience="mature",
    )
    created = create_project(proj_in)
    assert created.title == "Operation Borealis"
    assert created.id is not None

    fetched = get_project(created.id)
    assert fetched.id == created.id
    assert fetched.title == "Operation Borealis"

    all_projs = list_projects()
    assert any(p.id == created.id for p in all_projs)


def test_analysis_and_rewrite_pipeline():
    story_text = (
        "Marcus reached the bio-vault emergency console with seconds to spare. "
        "The automated defense voice echoed: 'Primary quarantine breached. T-minus ten seconds. "
        "Escape pods jettisoned.' This was an electrifying strong countdown ending."
    )
    proj_id = uuid4()
    req = AnalysisRequest(text=story_text)

    # 1. Analyze
    analysis_res = analyze_cliffhanger(project_id=proj_id, payload=req)
    assert analysis_res.final_score > 70.0
    assert analysis_res.score_band in ["Strong", "Very Strong", "Exceptional"]
    assert len(analysis_res.dimension_breakdown) == 9
    assert len(analysis_res.taxonomy_classifications) > 0
    assert len(analysis_res.evidence_quotes) > 0

    analysis_id = analysis_res.analysis_id

    # 2. Get Analysis
    retrieved = get_analysis(analysis_id)
    assert retrieved.analysis_id == analysis_id
    assert retrieved.final_score == analysis_res.final_score

    # 3. Generate Rewrite
    rewrite_req = RewriteRequest(
        analysis_id=analysis_id,
        target_dimension="urgency",
        style="intensified",
    )
    rewrite_res = generate_rewrite(analysis_id=analysis_id, payload=rewrite_req)
    assert rewrite_res.analysis_id == analysis_id
    assert rewrite_res.target_dimension == "urgency"
    assert rewrite_res.predicted_score >= analysis_res.final_score
    assert rewrite_res.is_consistent is True

    # 4. List Rewrites
    rewrites_list = list_rewrites(analysis_id)
    assert len(rewrites_list) >= 1
    assert rewrites_list[0].rewrite_id == rewrite_res.rewrite_id


def test_benchmark_runner_route():
    result = run_benchmarks()
    assert result.sample_count > 0
    assert result.regression_passed is True
    assert result.spearman_correlation > 0.80
    assert result.mean_absolute_error < 15.0


def test_root_web_ui():
    from apps.api.main import index_ui
    html = index_ui()
    assert "Cliffhanger Strength Analyzer" in html
    assert "Analyze Cliffhanger Strength" in html
    assert "Phase 5: Rewrite Laboratory" in html
