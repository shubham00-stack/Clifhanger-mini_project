"""Mathematical metric calculators for Phase 6 evaluation benchmarks."""

import math
from typing import Dict, List, Set, Tuple


def calculate_mae(predictions: List[float], ground_truths: List[float]) -> float:
    """Computes Mean Absolute Error between predicted and ground truth scores."""
    if not predictions or len(predictions) != len(ground_truths):
        raise ValueError("Predictions and ground truths must be non-empty and of equal length")
    total_abs_error = sum(abs(p - gt) for p, gt in zip(predictions, ground_truths))
    return round(total_abs_error / len(predictions), 3)


def _compute_ranks(values: List[float]) -> List[float]:
    """Computes fractional ranks handling ties with high numerical precision."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    n = len(values)
    while i < n:
        j = i
        while j < n - 1 and math.isclose(indexed[j][1], indexed[j + 1][1], abs_tol=1e-7):
            j += 1
        # Average rank for tied values (1-based index)
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def calculate_spearman_correlation(predictions: List[float], ground_truths: List[float]) -> float:
    """Computes Spearman Rank Correlation Coefficient (r_s) with tie correction."""
    if len(predictions) < 2 or len(predictions) != len(ground_truths):
        raise ValueError("Need at least 2 pairs of values for Spearman correlation")

    r_x = _compute_ranks(predictions)
    r_y = _compute_ranks(ground_truths)

    mean_x = sum(r_x) / len(r_x)
    mean_y = sum(r_y) / len(r_y)

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(r_x, r_y))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in r_x))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in r_y))

    if den_x == 0.0 or den_y == 0.0:
        return 0.0

    return round(num / (den_x * den_y), 4)


def calculate_taxonomy_precision_recall_f1(
    predicted_label_sets: List[List[str]],
    ground_truth_label_sets: List[List[str]],
) -> Dict[str, float]:
    """Computes micro-averaged Precision, Recall, and F1 across multi-label classifications."""
    if len(predicted_label_sets) != len(ground_truth_label_sets):
        raise ValueError("Predicted and ground truth label sets must match in length")

    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for preds, gts in zip(predicted_label_sets, ground_truth_label_sets):
        pred_set = {str(p).strip().lower() for p in preds}
        gt_set = {str(g).strip().lower() for g in gts}

        tp = len(pred_set.intersection(gt_set))
        fp = len(pred_set - gt_set)
        fn = len(gt_set - pred_set)

        true_positives += tp
        false_positives += fp
        false_negatives += fn

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def calculate_citation_accuracy(
    extracted_quotes: List[str],
    source_text: str,
) -> float:
    """
    Computes exact citation accuracy: percentage of extracted quotes that exist
    verbatim in the canonical narrative source text.
    """
    if not extracted_quotes:
        return 1.0

    valid_count = 0
    normalized_source = " ".join(source_text.split())

    for quote in extracted_quotes:
        cleaned_quote = " ".join(quote.strip().strip('"\'').split())
        if cleaned_quote in normalized_source:
            valid_count += 1

    return round(valid_count / len(extracted_quotes), 4)
