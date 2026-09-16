"""
BMW Data Quality & Governance Platform — Quality Score Calculator
Participant 12 | Pod D
Weighted scoring: 100 - Σ(violation_rate × weight)
"""

from src.utils.config import SCORING_WEIGHTS, get_score_label
from src.processing.quality_engine import QualityMetrics


class QualityScoreCalculator:
    """
    Computes the 0–100 Data Quality Score from QualityMetrics.

    Scoring formula:
        score = 100 - Σ (violation_rate_i × weight_i)

    Where violation_rate_i = violations_i / total_records

    Weights (configurable in config.py):
        null_check            20
        duplicate_check       15
        vin_check             20
        date_check            15
        range_check           15
        referential_integrity 15
        ─────────────────────────
        Total                100
    """

    def __init__(self, weights: dict | None = None):
        self.weights = weights or SCORING_WEIGHTS

    def calculate(self, metrics: QualityMetrics) -> tuple[float, str, dict]:
        """
        Calculate the quality score.

        Args:
            metrics: QualityMetrics object from QualityEngine.

        Returns:
            (score, label, penalty_breakdown)
        """
        total = max(metrics.total_records, 1)  # guard against division by zero

        checks = {
            "null_check": metrics.null_count,
            "duplicate_check": metrics.duplicate_count,
            "vin_check": metrics.invalid_vin_count,
            "date_check": metrics.invalid_date_count,
            "range_check": metrics.range_violation_count,
            "referential_integrity": metrics.referential_error_count,
        }

        penalty_breakdown = {}
        total_penalty = 0.0

        for check_name, violation_count in checks.items():
            weight = self.weights.get(check_name, 0)
            violation_rate = min(violation_count / total, 1.0)
            penalty = round(violation_rate * weight, 4)
            penalty_breakdown[check_name] = {
                "violations": violation_count,
                "violation_rate_pct": round(violation_rate * 100, 2),
                "weight": weight,
                "penalty": penalty,
            }
            total_penalty += penalty

        score = max(0.0, round(100.0 - total_penalty, 2))
        label = get_score_label(score)

        return score, label, penalty_breakdown

    def apply_to_metrics(self, metrics: QualityMetrics) -> QualityMetrics:
        """Compute score and write it back to the metrics object."""
        score, label, _ = self.calculate(metrics)
        metrics.quality_score = score
        metrics.score_label = label
        return metrics
