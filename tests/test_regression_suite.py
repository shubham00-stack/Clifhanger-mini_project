"""Phase 6 regression test suite asserting Strong > Moderate > Weak narrative endings."""

import pytest
from evaluation.datasets.seed_suite import SEED_BENCHMARK_SUITE
from evaluation.benchmarks.runner import BenchmarkRunner


def test_regression_strong_greater_than_moderate_greater_than_weak():
    """
    Core Phase 6 deliverable:
    Automated regression gate verifying that Strong Endings consistently score higher
    than Moderate and Weak endings:
    Score_Strong > Score_Moderate > Score_Weak
    """
    runner = BenchmarkRunner()
    result = runner.run_suite(SEED_BENCHMARK_SUITE)

    assert result.regression_passed is True, "Regression test failed: Strong > Moderate > Weak constraint violated!"
    assert result.spearman_correlation > 0.85, f"Spearman rank correlation {result.spearman_correlation} below threshold 0.85"
    assert result.mean_absolute_error < 15.0, f"MAE {result.mean_absolute_error} above threshold 15.0"
    assert result.citation_accuracy >= 0.80, f"Citation accuracy {result.citation_accuracy} below threshold 80%"


def test_individual_triplet_rankings():
    """Verify that every weak ending scores below 50, and every strong ending scores above 65."""
    runner = BenchmarkRunner()
    result = runner.run_suite(SEED_BENCHMARK_SUITE)

    for item in result.details:
        level = item["target_level"]
        score = item["predicted_score"]
        if level == "weak":
            assert score < 50.0, f"Weak ending '{item['title']}' scored {score} (expected < 50.0)"
        elif level == "strong":
            assert score >= 65.0, f"Strong ending '{item['title']}' scored {score} (expected >= 65.0)"
        elif level == "moderate":
            assert 50.0 <= score <= 70.0, f"Moderate ending '{item['title']}' scored {score} (expected 50-70)"
