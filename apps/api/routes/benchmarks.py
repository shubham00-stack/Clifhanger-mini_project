"""Evaluation benchmark execution routes."""

from fastapi import APIRouter
from evaluation.benchmarks.runner import BenchmarkRunner
from packages.schemas.requests import BenchmarkEvaluationResult

router = APIRouter(prefix="/api/benchmarks", tags=["Benchmarks"])


@router.get("/run", response_model=BenchmarkEvaluationResult)
def run_benchmarks():
    """Runs ground truth benchmark suite and returns metrics."""
    runner = BenchmarkRunner()
    result = runner.run_suite()
    return result
