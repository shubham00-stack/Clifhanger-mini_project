"""Command-line benchmark suite runner."""

import json
import sys
from evaluation.benchmarks.runner import BenchmarkRunner


def main():
    runner = BenchmarkRunner()
    result = runner.run_suite()

    print("\n" + "=" * 65)
    print("      CLIFFHANGER STRENGTH ANALYZER - BENCHMARK REPORT")
    print("=" * 65)
    print(f"Dataset:              {result.dataset_name}")
    print(f"Total Samples:        {result.sample_count}")
    print(f"Mean Absolute Error:  {result.mean_absolute_error:.3f}")
    print(f"Spearman Correlation: {result.spearman_correlation:.4f}")
    print(f"Citation Accuracy:    {result.citation_accuracy * 100:.1f}%")
    print(f"Taxonomy Precision:   {result.taxonomy_precision * 100:.1f}%")
    print(f"Taxonomy Recall:      {result.taxonomy_recall * 100:.1f}%")
    print(f"Taxonomy F1-Score:    {result.taxonomy_f1 * 100:.1f}%")
    print(f"Regression Check:     {'PASSED (Strong > Mod > Weak)' if result.regression_passed else 'FAILED'}")
    print("-" * 65)

    print("\nSample Predictions:")
    for d in result.details:
        print(f"[{d['target_level'].upper():8s}] {d['title']:32s} | Pred: {d['predicted_score']:5.1f} | GT: {d['ground_truth_score']:5.1f} | Band: {d['predicted_band']}")

    print("=" * 65 + "\n")

    if not result.regression_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
