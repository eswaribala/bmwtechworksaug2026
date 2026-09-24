import csv
from collections import defaultdict
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "datasets"


def load_csv(filename: str):
    with (DATASET_DIR / filename).open(newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value: float, minimum: float, maximum: float) -> float:
    if maximum == minimum:
        return 1.0
    return (value - minimum) / (maximum - minimum)


def compute_2025_metrics():
    dealer_rows = load_csv("dealer.csv")
    sales_rows = load_csv("sales.csv")
    service_rows = load_csv("service.csv")
    feedback_rows = load_csv("customer_feedback.csv")

    revenue_by_dealer = defaultdict(float)
    for row in sales_rows:
        if row["sale_date"].startswith("2025-"):
            revenue_by_dealer[row["dealer_id"]] += float(row["quantity"]) * float(row["unit_price"])

    service_by_dealer = defaultdict(int)
    for row in service_rows:
        if row["service_date"].startswith("2025-"):
            service_by_dealer[row["dealer_id"]] += int(row["service_count"])

    ratings_by_dealer = defaultdict(list)
    for row in feedback_rows:
        if row["feedback_date"].startswith("2025-"):
            ratings_by_dealer[row["dealer_id"]].append(float(row["rating"]))

    metrics = []
    for dealer in dealer_rows:
        dealer_id = dealer["dealer_id"]
        revenue = revenue_by_dealer.get(dealer_id, 0.0)
        service_count = service_by_dealer.get(dealer_id, 0)
        ratings = ratings_by_dealer.get(dealer_id, [])
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0

        metrics.append(
            {
                "dealer_id": dealer_id,
                "dealer_name": dealer["dealer_name"],
                "region": dealer["region"],
                "revenue": revenue,
                "service_count": service_count,
                "average_rating": average_rating,
            }
        )

    return metrics


def compute_ranked_scores():
    metrics = compute_2025_metrics()

    revenue_values = [row["revenue"] for row in metrics]
    service_values = [row["service_count"] for row in metrics]
    rating_values = [row["average_rating"] for row in metrics]

    scored = []
    for row in metrics:
        normalized_revenue = normalize(row["revenue"], min(revenue_values), max(revenue_values))
        normalized_service = normalize(row["service_count"], min(service_values), max(service_values))
        normalized_rating = normalize(row["average_rating"], min(rating_values), max(rating_values))

        score = 100 * (
            0.50 * normalized_revenue
            + 0.30 * normalized_service
            + 0.20 * normalized_rating
        )
        scored.append(
            {
                "dealer_id": row["dealer_id"],
                "dealer_name": row["dealer_name"],
                "region": row["region"],
                "revenue": row["revenue"],
                "service_count": row["service_count"],
                "average_rating": row["average_rating"],
                "dealer_performance_score": round(score, 2),
            }
        )

    return sorted(scored, key=lambda item: item["dealer_performance_score"], reverse=True)


def test_dealer_master_contains_expected_records():
    dealers = load_csv("dealer.csv")

    assert len(dealers) == 10
    assert {dealer["dealer_id"] for dealer in dealers} == {f"D{index:03d}" for index in range(1, 11)}
    assert {dealer["region"] for dealer in dealers} == {"Europe", "Middle East", "North America", "Asia Pacific"}


def test_2025_score_ranking_matches_project_logic():
    ranked = compute_ranked_scores()

    assert [row["dealer_id"] for row in ranked[:3]] == ["D005", "D002", "D007"]
    assert ranked[0]["dealer_performance_score"] == pytest.approx(81.13)
    assert next(row for row in ranked if row["dealer_id"] == "D001")["dealer_performance_score"] == pytest.approx(27.5)
    assert next(row for row in ranked if row["dealer_id"] == "D009")["dealer_performance_score"] == pytest.approx(63.39)


def test_data_contains_2025_revenue_and_service_activity_for_each_dealer():
    metrics = compute_2025_metrics()

    assert len(metrics) == 10
    assert sum(row["revenue"] for row in metrics) == pytest.approx(27405900.0)
    assert sum(row["service_count"] for row in metrics) == 687
    assert sum(1 for row in metrics if row["average_rating"] > 0.0) == 10
