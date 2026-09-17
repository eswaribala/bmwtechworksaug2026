"""
Tests: Quality score calculation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.quality_engine import QualityMetrics
from src.scoring.quality_score import QualityScoreCalculator


def _make_metrics(null=0, dup=0, vin=0, date=0, rng=0, ref=0, total=10000):
    m = QualityMetrics(dataset='telemetry', total_records=total)
    m.null_count = null
    m.duplicate_count = dup
    m.invalid_vin_count = vin
    m.invalid_date_count = date
    m.range_violation_count = rng
    m.referential_error_count = ref
    return m


def test_perfect_dataset_scores_100():
    m = _make_metrics()
    calc = QualityScoreCalculator()
    score, label, _ = calc.calculate(m)
    assert score == 100.0
    assert label == 'EXCELLENT'


def test_demo_scenario_score_decreases_with_violations():
    """More violations → lower score than a perfect dataset."""
    m_perfect = _make_metrics(total=10000)
    m_dirty   = _make_metrics(null=210, dup=150, vin=80, date=60, rng=50, ref=30, total=10000)
    calc = QualityScoreCalculator()
    score_perfect, _, _ = calc.calculate(m_perfect)
    score_dirty,   _, _ = calc.calculate(m_dirty)
    assert score_perfect > score_dirty, "Dirty dataset should score lower"
    assert score_dirty > 90, "Small violation rates still produce high score"


def test_100_pct_violation_rate_each_check_scores_zero():
    """When every record violates every check the score is 0."""
    m = _make_metrics(null=10000, dup=10000, vin=10000, date=10000, rng=10000, ref=10000, total=10000)
    calc = QualityScoreCalculator()
    score, label, _ = calc.calculate(m)
    assert score == 0.0
    assert label == 'CRITICAL'


def test_score_label_excellent():
    m = _make_metrics(null=5, total=10000)
    calc = QualityScoreCalculator()
    score, label, _ = calc.calculate(m)
    assert label == 'EXCELLENT'


def test_score_never_below_zero():
    m = _make_metrics(null=10000, dup=10000, vin=10000, date=10000, rng=10000, ref=10000, total=10000)
    calc = QualityScoreCalculator()
    score, _, _ = calc.calculate(m)
    assert score >= 0.0


def test_penalty_breakdown_sums_correctly():
    m = _make_metrics(null=100, total=1000)
    calc = QualityScoreCalculator()
    score, _, breakdown = calc.calculate(m)
    total_penalty = sum(v['penalty'] for v in breakdown.values())
    assert abs(100 - total_penalty - score) < 0.01


def test_apply_to_metrics_mutates_object():
    m = _make_metrics(null=500, total=10000)
    calc = QualityScoreCalculator()
    result = calc.apply_to_metrics(m)
    assert result.quality_score > 0
    assert result.score_label != ''
