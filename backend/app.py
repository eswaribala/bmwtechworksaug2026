"""
BMW Data Quality & Governance Platform — FastAPI Backend
Participant 12 | Pod D

This server bridges the frontend CSV upload to the full AWS pipeline:
  1. Receives a CSV file via POST /upload
  2. Uploads it to S3 raw/<dataset>/
  3. Runs the data quality engine
  4. Saves curated / quarantine / reports to S3 (or local output/)
  5. Returns the full quality report JSON to the frontend

Usage:
    cd <project-root>
    uvicorn backend.app:app --reload --port 8000
"""

import io
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Project imports ────────────────────────────────────────────────
from src.utils.config import (
    S3_BUCKET, AWS_REGION,
    RAW_PREFIX, CURATED_PREFIX, QUARANTINE_PREFIX, REPORT_PREFIX,
)
from src.utils.logger import BmwLogger
from src.processing.quality_engine import QualityEngine
from src.processing.quarantine import QuarantineManager
from src.scoring.quality_score import QualityScoreCalculator
from src.reporting.quality_report import QualityReporter

# ────────────────────────────────────────────────────────────────────
# FastAPI app
# ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="BMW Data Quality & Governance Platform",
    description=(
        "Participant 12 — Validates BMW CSV datasets, runs quality checks, "
        "quarantines bad records, and returns a 0–100 quality score."
    ),
    version="1.0.0",
)

# Allow all origins so the Vite dev server can call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────────
# AWS S3 helper (graceful fallback when no AWS creds configured)
# ────────────────────────────────────────────────────────────────────

def _get_s3() -> Optional[object]:
    """Return boto3 S3 client, or None if AWS creds not available."""
    try:
        client = boto3.client("s3", region_name=AWS_REGION)
        # Test connectivity cheaply
        client.head_bucket(Bucket=S3_BUCKET)
        return client
    except Exception:
        return None


def _upload_bytes_to_s3(s3, data: bytes, key: str) -> str:
    """Upload raw bytes to S3 and return the s3:// URI."""
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=data)
    return f"s3://{S3_BUCKET}/{key}"


def _upload_df_to_s3(s3, df: pd.DataFrame, key: str) -> str:
    """Upload a DataFrame as CSV to S3."""
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue())
    return f"s3://{S3_BUCKET}/{key}"


def _upload_json_to_s3(s3, data: dict, key: str) -> str:
    """Upload a dict as JSON to S3."""
    body = json.dumps(data, indent=2, default=str).encode()
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/json")
    return f"s3://{S3_BUCKET}/{key}"


# ────────────────────────────────────────────────────────────────────
# Dataset detection (same logic as ValidatePage.tsx)
# ────────────────────────────────────────────────────────────────────

def detect_dataset(columns: list[str]) -> str:
    cols = set(c.lower() for c in columns)
    if "event_id" in cols:
        return "telemetry"
    if "vehicle_id" in cols or "vin" in cols:
        return "vehicle_master"
    return "unknown"


# ────────────────────────────────────────────────────────────────────
# Load vehicle master for referential integrity
# ────────────────────────────────────────────────────────────────────

def _load_vehicle_master(s3) -> Optional[pd.DataFrame]:
    """Try to load vehicle_master.csv from S3 raw/ or local data/sample/."""
    # 1. Try local sample first (fast, no AWS needed)
    local_path = PROJECT_ROOT / "data" / "sample" / "bmw_vehicle_master.csv"
    if local_path.exists():
        return pd.read_csv(local_path)

    # 2. Try S3
    if s3:
        try:
            key = f"{RAW_PREFIX}/vehicle_master/vehicle_master.csv"
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
            return pd.read_csv(io.BytesIO(obj["Body"].read()))
        except Exception:
            pass
    return None


# ────────────────────────────────────────────────────────────────────
# Core pipeline runner
# ────────────────────────────────────────────────────────────────────

def run_pipeline_on_df(
    df: pd.DataFrame,
    dataset: str,
    filename: str,
    s3,
) -> dict:
    """
    Run the full BMW data quality pipeline on an already-loaded DataFrame.
    Returns the quality report dict.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logger = BmwLogger(dataset)

    # ── 1. Load vehicle master for referential integrity ───────
    reference_df = _load_vehicle_master(s3)

    # ── 2. Quality engine ──────────────────────────────────────
    engine = QualityEngine(dataset=dataset, logger=logger)
    valid_df, invalid_df, metrics = engine.run(df, reference_df=reference_df)

    # ── 3. Quality score ───────────────────────────────────────
    scorer = QualityScoreCalculator()
    scorer.apply_to_metrics(metrics)

    # ── 4. Quality report ──────────────────────────────────────
    reporter = QualityReporter(calculator=scorer)
    text_report, json_report = reporter.generate(metrics)

    # ── 5. Quarantine ──────────────────────────────────────────
    qm = QuarantineManager(dataset=dataset, logger=logger)
    quarantine_df = qm.prepare(invalid_df)

    # ── 6. Save outputs ────────────────────────────────────────
    s3_paths: dict[str, str] = {}
    local_base = PROJECT_ROOT / "output"

    if s3:
        # Upload curated
        curated_key = f"{CURATED_PREFIX}/{dataset}/{ts}_{dataset}_curated.csv"
        s3_paths["curated"] = _upload_df_to_s3(s3, valid_df, curated_key)

        # Upload quarantine
        if len(quarantine_df) > 0:
            quarantine_key = f"{QUARANTINE_PREFIX}/{dataset}/{ts}_{dataset}_quarantine.csv"
            s3_paths["quarantine"] = _upload_df_to_s3(s3, quarantine_df, quarantine_key)

        # Upload JSON report
        report_key = f"{REPORT_PREFIX}/{dataset}/{ts}_{dataset}_quality_report.json"
        s3_paths["report"] = _upload_json_to_s3(s3, json_report, report_key)

        # Upload text report
        txt_key = f"{REPORT_PREFIX}/{dataset}/{ts}_{dataset}_quality_report.txt"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=txt_key,
            Body=text_report.encode(),
            ContentType="text/plain",
        )
    else:
        # Local fallback
        for subdir in ["curated", "quarantine", "reports"]:
            (local_base / subdir).mkdir(parents=True, exist_ok=True)

        curated_path = local_base / "curated" / f"{ts}_{dataset}_curated.csv"
        valid_df.to_csv(curated_path, index=False)
        s3_paths["curated"] = str(curated_path)

        if len(quarantine_df) > 0:
            quarantine_path = local_base / "quarantine" / f"{ts}_{dataset}_quarantine.csv"
            quarantine_df.to_csv(quarantine_path, index=False)
            s3_paths["quarantine"] = str(quarantine_path)

        report_path = local_base / "reports" / f"{ts}_{dataset}_quality_report.json"
        report_path.write_text(json.dumps(json_report, indent=2, default=str))
        txt_path = local_base / "reports" / f"{ts}_{dataset}_quality_report.txt"
        txt_path.write_text(text_report)
        s3_paths["report"] = str(report_path)

    # ── 7. CloudWatch logging ──────────────────────────────────
    try:
        from src.monitoring.cloudwatch_logger import CloudWatchLogger
        cw = CloudWatchLogger(dataset=dataset, logger=logger)
        logger.pipeline_end()
        cw.upload_logs(logger.get_logs())
        cw.put_metric("QualityScore", metrics.quality_score, "None")
        cw.put_metric("RejectedRecords", metrics.rejected_records, "Count")
        cw.put_metric("ValidRecords", metrics.valid_records, "Count")
    except Exception:
        pass  # CloudWatch is optional — don't fail the whole request

    return {
        **json_report,
        "dataset": dataset,
        "quality_score": metrics.quality_score,
        "score_label": metrics.score_label,
        "total_records": metrics.total_records,
        "valid_records": metrics.valid_records,
        "rejected_records": metrics.rejected_records,
        "null_count": metrics.null_count,
        "duplicate_count": metrics.duplicate_count,
        "invalid_vin_count": metrics.invalid_vin_count,
        "invalid_date_count": metrics.invalid_date_count,
        "range_violation_count": metrics.range_violation_count,
        "referential_error_count": metrics.referential_error_count,
        "null_summary": metrics.null_summary,
        "penalty_breakdown": json_report.get("bmw_data_quality_report", {}).get("penalty_breakdown", {}),
        "s3_paths": s3_paths,
        "text_report": text_report,
        "aws_connected": s3 is not None,
        "raw_s3_path": (
            f"s3://{S3_BUCKET}/{RAW_PREFIX}/{dataset}/{filename}"
            if s3 else None
        ),
    }


# ────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check — also reports AWS connectivity."""
    s3 = _get_s3()
    return {
        "status": "ok",
        "service": "BMW Data Quality Platform",
        "aws_connected": s3 is not None,
        "s3_bucket": S3_BUCKET,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Main endpoint — accepts a BMW CSV file, runs the quality pipeline,
    and returns the full quality report JSON.

    Flow:
      CSV → S3 raw/ → Quality Engine → Curated + Quarantine → Report
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    # Read file bytes
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Parse CSV
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV has no data rows")

    # Detect dataset type
    dataset = detect_dataset(list(df.columns))

    # Try to get S3 client (non-blocking — falls back to local)
    s3 = _get_s3()

    # Upload raw CSV to S3
    if s3:
        raw_key = f"{RAW_PREFIX}/{dataset}/{file.filename}"
        try:
            _upload_bytes_to_s3(s3, raw_bytes, raw_key)
        except Exception:
            s3 = None  # Fallback to local if upload fails

    # Run the quality pipeline
    try:
        report = run_pipeline_on_df(
            df=df,
            dataset=dataset,
            filename=file.filename,
            s3=s3,
        )
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "traceback": tb},
        )

    return JSONResponse(content=report)


@app.get("/results/{dataset}")
async def get_latest_result(dataset: str):
    """
    Fetch the latest quality report for a dataset from S3 reports/.
    Falls back to output/reports/ if AWS not configured.
    """
    s3 = _get_s3()

    if s3:
        try:
            prefix = f"{REPORT_PREFIX}/{dataset}/"
            resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
            objects = sorted(
                resp.get("Contents", []),
                key=lambda o: o["LastModified"],
                reverse=True,
            )
            json_objects = [o for o in objects if o["Key"].endswith(".json")]
            if not json_objects:
                raise HTTPException(status_code=404, detail=f"No reports found for dataset '{dataset}'")

            obj = s3.get_object(Bucket=S3_BUCKET, Key=json_objects[0]["Key"])
            data = json.loads(obj["Body"].read().decode())
            data["source"] = f"s3://{S3_BUCKET}/{json_objects[0]['Key']}"
            return JSONResponse(content=data)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Local fallback
        local_dir = PROJECT_ROOT / "output" / "reports"
        reports = sorted(local_dir.glob(f"*{dataset}*_quality_report.json"), reverse=True)
        if not reports:
            raise HTTPException(status_code=404, detail=f"No local reports found for dataset '{dataset}'")
        data = json.loads(reports[0].read_text())
        data["source"] = str(reports[0])
        return JSONResponse(content=data)
