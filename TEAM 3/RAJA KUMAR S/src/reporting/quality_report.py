"""
BMW Data Quality & Governance Platform — Quality Report Generator
Participant 12 | Pod D
"""

from src.processing.quality_engine import QualityMetrics
from src.scoring.quality_score import QualityScoreCalculator


_SEPARATOR = "=" * 52
_DIVIDER = "-" * 52


def generate_text_report(metrics: QualityMetrics, penalty_breakdown: dict) -> str:
    """Return the quality report as a formatted text string."""
    lines = [
        _SEPARATOR,
        "        BMW DATA QUALITY REPORT",
        _SEPARATOR,
        "",
        f"  Dataset              : {metrics.dataset.title()}",
        f"  Execution Time       : {metrics.execution_time[:19].replace('T', ' ')}",
        f"  Processing Duration  : {metrics.duration_seconds:.3f}s",
        "",
        _DIVIDER,
        "  RECORD SUMMARY",
        _DIVIDER,
        "",
        f"  Total Records        : {metrics.total_records:>10,}",
        f"  Valid Records        : {metrics.valid_records:>10,}",
        f"  Rejected Records     : {metrics.rejected_records:>10,}",
        "",
        _DIVIDER,
        "  QUALITY CHECKS",
        _DIVIDER,
        "",
        f"  Null Issues          : {metrics.null_count:>10,}",
        f"  Duplicate Records    : {metrics.duplicate_count:>10,}",
        f"  Invalid VIN          : {metrics.invalid_vin_count:>10,}",
        f"  Invalid Dates        : {metrics.invalid_date_count:>10,}",
        f"  Out-of-Range Values  : {metrics.range_violation_count:>10,}",
        f"  Referential Errors   : {metrics.referential_error_count:>10,}",
        "",
        _DIVIDER,
        "  SCORING BREAKDOWN",
        _DIVIDER,
        "",
    ]

    for check, detail in penalty_breakdown.items():
        label = check.replace("_", " ").title()
        lines.append(
            f"  {label:<26}: rate={detail['violation_rate_pct']:>5.1f}%  "
            f"weight={detail['weight']:>2}  penalty={detail['penalty']:>6.2f}"
        )

    lines += [
        "",
        _DIVIDER,
        "  QUALITY SCORE",
        _DIVIDER,
        "",
        f"  Score                : {metrics.quality_score:>6.1f} / 100",
        f"  Status               : {metrics.score_label}",
        "",
        _SEPARATOR,
    ]

    if metrics.null_summary:
        lines += ["", _DIVIDER, "  NULL ANALYSIS", _DIVIDER, ""]
        lines.append(f"  {'Column':<30} {'Null Count':>12} {'Null %':>8}")
        lines.append(f"  {'-'*30} {'-'*12} {'-'*8}")
        for item in metrics.null_summary:
            lines.append(
                f"  {item['column']:<30} {item['null_count']:>12,} {item['null_pct']:>7.2f}%"
            )
        lines.append("")

    return "\n".join(lines)


def generate_json_report(metrics: QualityMetrics, penalty_breakdown: dict) -> dict:
    """Return the quality report as a JSON-serialisable dict."""
    return {
        "bmw_data_quality_report": {
            "dataset": metrics.dataset,
            "execution_time": metrics.execution_time,
            "duration_seconds": metrics.duration_seconds,
            "record_summary": {
                "total_records": metrics.total_records,
                "valid_records": metrics.valid_records,
                "rejected_records": metrics.rejected_records,
            },
            "quality_checks": {
                "null_issues": metrics.null_count,
                "duplicate_records": metrics.duplicate_count,
                "invalid_vin": metrics.invalid_vin_count,
                "invalid_dates": metrics.invalid_date_count,
                "range_violations": metrics.range_violation_count,
                "referential_errors": metrics.referential_error_count,
            },
            "quality_score": metrics.quality_score,
            "score_label": metrics.score_label,
            "penalty_breakdown": penalty_breakdown,
            "null_analysis": metrics.null_summary,
        }
    }


class QualityReporter:
    """Orchestrates report generation and persistence."""

    def __init__(self, calculator: QualityScoreCalculator | None = None):
        self.calculator = calculator or QualityScoreCalculator()

    def generate(self, metrics: QualityMetrics) -> tuple[str, dict]:
        """
        Calculate the score, generate text and JSON reports.

        Returns:
            (text_report, json_report_dict)
        """
        score, label, breakdown = self.calculator.calculate(metrics)
        metrics.quality_score = score
        metrics.score_label = label

        text = generate_text_report(metrics, breakdown)
        data = generate_json_report(metrics, breakdown)
        return text, data
