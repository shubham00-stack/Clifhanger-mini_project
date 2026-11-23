"""Multi-label Cliffhanger Taxonomy Classifier and Calibration."""

from typing import Any, Dict, List
from packages.schemas.enums import CliffhangerType


VALID_TAXONOMY_TYPES = {t.value for t in CliffhangerType}


def calibrate_and_filter_taxonomy(
    raw_classifications: List[Dict[str, Any]],
    confidence_threshold: float = 0.40,
    max_labels: int = 4,
) -> List[Dict[str, Any]]:
    """
    Validates, calibrates, and filters taxonomy classifications against the 12 recognized types.
    Sorts by confidence descending and caps at max_labels.
    """
    calibrated = []
    for item in raw_classifications:
        raw_type = str(item.get("type", "")).strip().lower()
        if raw_type not in VALID_TAXONOMY_TYPES:
            continue

        raw_conf = float(item.get("confidence", 0.5))
        clamped_conf = max(0.0, min(1.0, raw_conf))

        if clamped_conf >= confidence_threshold:
            calibrated.append({
                "type": raw_type,
                "confidence": round(clamped_conf, 2),
                "rationale": str(item.get("rationale", "")),
            })

    # Sort descending by confidence
    calibrated.sort(key=lambda x: x["confidence"], reverse=True)
    return calibrated[:max_labels]
