"""Executive analysis report generator (Markdown & JSON export formats)."""

import json
from typing import Any, Dict
from packages.schemas.requests import AnalysisResponse


class ReportGenerator:
    """Generates structured executive reports for showrunners and authors."""

    @staticmethod
    def generate_markdown(response: AnalysisResponse) -> str:
        lines = [
            f"# Cliffhanger Strength Evaluation Report",
            f"**Analysis ID:** `{response.analysis_id}`  ",
            f"**Overall Score:** **{response.final_score:.1f} / 100**  ",
            f"**Score Band:** `{response.score_band.value}`  ",
            f"**Evaluator Model:** `{response.model_name}` (Prompt `{response.prompt_version}`)  ",
            "",
            "## Dimension Ratings Breakdown",
            "| Dimension | Score | Weight | Contribution | Confidence |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        for item in response.dimension_breakdown:
            lines.append(
                f"| `{item.dimension_name}` | {item.score:.1f} | {int(item.weight * 100)}% | {item.weighted_contribution:.2f} | {int(item.confidence * 100)}% |"
            )

        lines.extend([
            "",
            "## Multi-Label Taxonomy Classifications",
        ])
        for tax in response.taxonomy_classifications:
            lines.append(f"- **{tax.get('type', '').upper()}** ({int(tax.get('confidence', 0.0) * 100)}%): {tax.get('rationale', '')}")

        lines.extend([
            "",
            "## Verified Evidence Citations",
        ])
        for ev in response.evidence_quotes:
            lines.append(f"> \"{ev.get('quote', '')}\" — *{ev.get('location', 'ending')}* (Relevance: {ev.get('relevance', 0.9):.2f})")

        if response.open_questions:
            lines.extend([
                "",
                "## Critical Unresolved Questions",
            ])
            for q in response.open_questions:
                lines.append(f"- {q}")

        return "\n".join(lines)

    @staticmethod
    def generate_json(response: AnalysisResponse) -> str:
        return json.dumps(response.model_dump(), default=str, indent=2)
