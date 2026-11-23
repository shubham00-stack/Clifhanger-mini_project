"""Unit tests for Phase 6 evaluation benchmark metrics."""

import pytest
from evaluation.benchmarks.metrics import (
    calculate_mae,
    calculate_spearman_correlation,
    calculate_taxonomy_precision_recall_f1,
    calculate_citation_accuracy,
)


def test_mae_calculation():
    preds = [80.0, 60.0, 40.0]
    gts = [82.0, 58.0, 41.0]
    mae = calculate_mae(preds, gts)
    assert mae == round((2.0 + 2.0 + 1.0) / 3, 3)


def test_spearman_rank_correlation_perfect():
    preds = [10.0, 20.0, 30.0, 40.0, 50.0]
    gts = [15.0, 25.0, 35.0, 45.0, 55.0]
    corr = calculate_spearman_correlation(preds, gts)
    assert abs(corr - 1.0) < 1e-4


def test_spearman_rank_correlation_inverse():
    preds = [50.0, 40.0, 30.0, 20.0, 10.0]
    gts = [10.0, 20.0, 30.0, 40.0, 50.0]
    corr = calculate_spearman_correlation(preds, gts)
    assert abs(corr - (-1.0)) < 1e-4


def test_spearman_with_tied_ranks():
    preds = [10.0, 20.0, 20.0, 40.0]
    gts = [5.0, 15.0, 25.0, 35.0]
    corr = calculate_spearman_correlation(preds, gts)
    assert corr > 0.90


def test_taxonomy_precision_recall_f1():
    preds = [["threat", "countdown"], ["mystery"]]
    gts = [["threat", "countdown"], ["mystery", "revelation"]]

    metrics = calculate_taxonomy_precision_recall_f1(preds, gts)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.75
    assert metrics["f1"] == round((2 * 1.0 * 0.75) / (1.0 + 0.75), 4)


def test_citation_accuracy():
    source = "The digital timer flashed 00:03, humming with high-voltage frequency."
    quotes = [
        "The digital timer flashed 00:03",
        "This quote never happened anywhere in the text",
    ]
    acc = calculate_citation_accuracy(quotes, source)
    assert acc == 0.5
