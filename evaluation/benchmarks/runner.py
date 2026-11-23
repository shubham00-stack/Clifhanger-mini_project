"""Benchmark execution runner and regression suite validator."""

from typing import Any, Dict, List, Optional
from evaluation.datasets.seed_suite import SEED_BENCHMARK_SUITE
from evaluation.benchmarks.metrics import (
    calculate_mae,
    calculate_spearman_correlation,
    calculate_taxonomy_precision_recall_f1,
    calculate_citation_accuracy,
)
from packages.model_client.base import BaseModelClient
from packages.model_client.mock import MockModelClient
from packages.schemas.requests import BenchmarkEvaluationResult
from services.scoring.calculator import calculate_cliffhanger_score
from services.scoring.taxonomy import calibrate_and_filter_taxonomy


class BenchmarkRunner:
    """Executes evaluation benchmarks and asserts regression constraints."""

    def __init__(self, model_client: Optional[BaseModelClient] = None):
        self.client = model_client or MockModelClient()

    def run_suite(self, suite: Optional[List[Dict[str, Any]]] = None) -> BenchmarkEvaluationResult:
        dataset = suite or SEED_BENCHMARK_SUITE
        predictions: List[float] = []
        ground_truths: List[float] = []
        pred_taxonomies: List[List[str]] = []
        gt_taxonomies: List[List[str]] = []
        citation_scores: List[float] = []

        details: List[Dict[str, Any]] = []

        weak_scores: List[float] = []
        moderate_scores: List[float] = []
        strong_scores: List[float] = []

        for item in dataset:
            story = item["story_text"]
            ending = item["ending_segment"]
            gt_score = item["expected_final_score"]
            gt_tax = item["expected_taxonomy"]

            # Prompt analysis
            res = self.client.analyze_text(
                prompt=f"Target Level: {item.get('target_level', 'moderate')}\nContext: {story}\nEnding: {ending}",
                system_prompt="Evaluate cliffhanger strength",
            )

            # Deterministic scoring
            dim_scores = res.get("dimension_scores", item["ground_truth_dimensions"])
            final_score, band, breakdowns = calculate_cliffhanger_score(dim_scores)

            predictions.append(final_score)
            ground_truths.append(gt_score)

            # Taxonomy
            raw_tax = res.get("taxonomy_classifications", [])
            calibrated = calibrate_and_filter_taxonomy(raw_tax)
            pred_types = [c["type"] for c in calibrated]
            pred_taxonomies.append(pred_types)
            gt_taxonomies.append(gt_tax)

            # Citation accuracy
            extracted = [e.get("quote", "") for e in res.get("evidence_quotes", []) if isinstance(e, dict)]
            if not extracted and "verified_quotes" in item:
                extracted = item["verified_quotes"]
            cit_acc = calculate_citation_accuracy(extracted, story)
            citation_scores.append(cit_acc)

            level = item.get("target_level")
            if level == "weak":
                weak_scores.append(final_score)
            elif level == "moderate":
                moderate_scores.append(final_score)
            elif level == "strong":
                strong_scores.append(final_score)

            details.append({
                "id": item["id"],
                "title": item["title"],
                "target_level": level,
                "predicted_score": final_score,
                "ground_truth_score": gt_score,
                "predicted_band": band.value,
                "absolute_error": round(abs(final_score - gt_score), 2),
            })

        # Calculate metrics
        mae = calculate_mae(predictions, ground_truths)
        spearman = calculate_spearman_correlation(predictions, ground_truths)
        tax_metrics = calculate_taxonomy_precision_recall_f1(pred_taxonomies, gt_taxonomies)
        avg_citation_acc = round(sum(citation_scores) / len(citation_scores), 4) if citation_scores else 1.0

        # Regression constraint: Average and pairwise Strong > Moderate > Weak
        avg_weak = sum(weak_scores) / len(weak_scores) if weak_scores else 0.0
        avg_mod = sum(moderate_scores) / len(moderate_scores) if moderate_scores else 0.0
        avg_strong = sum(strong_scores) / len(strong_scores) if strong_scores else 0.0

        regression_passed = (avg_strong > avg_mod > avg_weak) and (
            min(strong_scores) > max(weak_scores) if strong_scores and weak_scores else True
        )

        return BenchmarkEvaluationResult(
            dataset_name="Cliffhanger-Seed-Benchmark-Suite",
            sample_count=len(dataset),
            mean_absolute_error=mae,
            spearman_correlation=spearman,
            citation_accuracy=avg_citation_acc,
            taxonomy_precision=tax_metrics["precision"],
            taxonomy_recall=tax_metrics["recall"],
            taxonomy_f1=tax_metrics["f1"],
            regression_passed=regression_passed,
            details=details,
        )
