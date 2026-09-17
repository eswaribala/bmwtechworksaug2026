"""
BMW Data Quality & Governance Platform — Configuration
Participant 12 | Pod D
"""

import os

# ────────────────────────────────────────────────
# AWS / S3
# ────────────────────────────────────────────────
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
S3_BUCKET = os.getenv("S3_BUCKET", "bmw-data-quality-532404260630")
RAW_PREFIX = os.getenv("RAW_PREFIX", "raw")
PROCESSED_PREFIX = os.getenv("PROCESSED_PREFIX", "processed")
CURATED_PREFIX = os.getenv("CURATED_PREFIX", "curated")
QUARANTINE_PREFIX = os.getenv("QUARANTINE_PREFIX", "quarantine")
REPORT_PREFIX = os.getenv("REPORT_PREFIX", "reports")
LOG_PREFIX = os.getenv("LOG_PREFIX", "logs")

# ────────────────────────────────────────────────
# AWS Glue / Athena
# ────────────────────────────────────────────────
GLUE_DATABASE = os.getenv("GLUE_DATABASE", "bmw_data_quality")
ATHENA_WORKGROUP = os.getenv("ATHENA_WORKGROUP", "bmw-data-quality")
ATHENA_OUTPUT_LOCATION = os.getenv(
    "ATHENA_OUTPUT_LOCATION", f"s3://{S3_BUCKET}/reports/athena-results/"
)

# ────────────────────────────────────────────────
# Datasets
# ────────────────────────────────────────────────
DATASETS = ["vehicle_master", "telemetry"]

REQUIRED_COLUMNS = {
    "vehicle_master": ["vehicle_id", "vin", "model", "model_year", "region", "status"],
    "telemetry": ["event_id", "vehicle_id", "vin", "timestamp", "battery_level", "speed", "temperature"],
    "sales": ["sale_id", "vehicle_id", "vin", "sale_date", "region", "dealer_id"],
    "maintenance": ["service_id", "vehicle_id", "service_date", "service_type"],
    "warranty": ["claim_id", "vehicle_id", "claim_date", "claim_type"],
    "charging": ["session_id", "vehicle_id", "start_time", "end_time", "energy_kwh"],
}

UNIQUE_KEY_COLUMNS = {
    "vehicle_master": ["vehicle_id"],
    "telemetry": ["event_id"],
    "sales": ["sale_id"],
    "maintenance": ["service_id"],
    "warranty": ["claim_id"],
    "charging": ["session_id"],
}

DATE_COLUMNS = {
    "vehicle_master": [],
    "telemetry": ["timestamp"],
    "sales": ["sale_date"],
    "maintenance": ["service_date"],
    "warranty": ["claim_date"],
    "charging": ["start_time", "end_time"],
}

# ────────────────────────────────────────────────
# VIN Validation
# ────────────────────────────────────────────────
VIN_REGEX = r"^[A-HJ-NPR-Z0-9]{17}$"
VIN_COLUMN = "vin"

# ────────────────────────────────────────────────
# Out-of-Range Rules  {column: (min, max)}
# ────────────────────────────────────────────────
RANGE_RULES = {
    "battery_level": (0.0, 100.0),
    "temperature": (-40.0, 120.0),
    "speed": (0.0, 300.0),
    "rating": (1.0, 5.0),
    "energy_kwh": (0.0, 200.0),
}

# ────────────────────────────────────────────────
# Referential Integrity Rules
# {child_dataset: (child_fk_col, parent_dataset, parent_pk_col)}
# ────────────────────────────────────────────────
REFERENTIAL_RULES = {
    "telemetry": ("vehicle_id", "vehicle_master", "vehicle_id"),
    "sales": ("vehicle_id", "vehicle_master", "vehicle_id"),
    "maintenance": ("vehicle_id", "vehicle_master", "vehicle_id"),
    "warranty": ("vehicle_id", "vehicle_master", "vehicle_id"),
    "charging": ("vehicle_id", "vehicle_master", "vehicle_id"),
}

# ────────────────────────────────────────────────
# Scoring Weights (must sum to 100)
# ────────────────────────────────────────────────
SCORING_WEIGHTS = {
    "null_check": 20,
    "duplicate_check": 15,
    "vin_check": 20,
    "date_check": 15,
    "range_check": 15,
    "referential_integrity": 15,
}

# ────────────────────────────────────────────────
# Quality Score Thresholds
# ────────────────────────────────────────────────
SCORE_THRESHOLDS = {
    "excellent": 90,
    "good": 80,
    "acceptable": 70,
    "poor": 50,
    "critical": 0,
}

SCORE_LABELS = {
    "excellent": "EXCELLENT",
    "good": "GOOD",
    "acceptable": "ACCEPTABLE",
    "poor": "POOR",
    "critical": "CRITICAL",
}


def get_score_label(score: float) -> str:
    """Return a human-readable quality label for a given score."""
    if score >= SCORE_THRESHOLDS["excellent"]:
        return SCORE_LABELS["excellent"]
    elif score >= SCORE_THRESHOLDS["good"]:
        return SCORE_LABELS["good"]
    elif score >= SCORE_THRESHOLDS["acceptable"]:
        return SCORE_LABELS["acceptable"]
    elif score >= SCORE_THRESHOLDS["poor"]:
        return SCORE_LABELS["poor"]
    return SCORE_LABELS["critical"]


# ────────────────────────────────────────────────
# CloudWatch
# ────────────────────────────────────────────────
CLOUDWATCH_LOG_GROUP = "/bmw/data-quality"
CLOUDWATCH_LOG_STREAM_PREFIX = "pipeline"
