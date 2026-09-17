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
import time
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
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Project imports ────────────────────────────────────────────────
from src.utils.config import (
    S3_BUCKET, AWS_REGION,
    RAW_PREFIX, CURATED_PREFIX, QUARANTINE_PREFIX, REPORT_PREFIX, LOG_PREFIX,
    GLUE_DATABASE, ATHENA_WORKGROUP, ATHENA_OUTPUT_LOCATION,
)
from src.utils.logger import BmwLogger
from src.utils.spark_session import get_spark
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


def _get_glue() -> Optional[object]:
    """Return boto3 Glue client, or None if AWS creds not available."""
    try:
        return boto3.client("glue", region_name=AWS_REGION)
    except Exception:
        return None


def _get_athena() -> Optional[object]:
    """Return boto3 Athena client, or None if AWS creds not available."""
    try:
        return boto3.client("athena", region_name=AWS_REGION)
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


def _get_s3_json(s3, key: str) -> Optional[dict]:
    """Download and parse a JSON object from S3, or None if missing/unreadable."""
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return json.loads(obj["Body"].read().decode())
    except Exception:
        return None


def _get_s3_text(s3, key: str) -> Optional[str]:
    """Download a text object from S3, or None if missing/unreadable."""
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return obj["Body"].read().decode()
    except Exception:
        return None


def _get_s3_csv(s3, key: str) -> Optional[pd.DataFrame]:
    """Download and parse a CSV object from S3 into a DataFrame, or None if missing."""
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(obj["Body"].read()))
    except Exception:
        return None


def _ensure_glue_tables(glue) -> None:
    """
    Idempotently ensure the Glue Catalog has the tables required for real
    Athena querying: quarantine_telemetry (created on demand) and
    data_quality_report (location corrected to the flat JSON summary prefix).
    """
    if not glue:
        return

    # ── quarantine_telemetry ─────────────────────────────────
    try:
        glue.get_table(DatabaseName=GLUE_DATABASE, Name="quarantine_telemetry")
    except Exception:
        try:
            glue.create_table(
                DatabaseName=GLUE_DATABASE,
                TableInput={
                    "Name": "quarantine_telemetry",
                    "TableType": "EXTERNAL_TABLE",
                    "Parameters": {"classification": "csv", "skip.header.line.count": "1"},
                    "StorageDescriptor": {
                        "Location": f"s3://{S3_BUCKET}/{QUARANTINE_PREFIX}/telemetry/",
                        "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                        "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                        "SerdeInfo": {
                            "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                            "Parameters": {"field.delim": ",", "skip.header.line.count": "1"},
                        },
                        "Columns": [
                            {"Name": c, "Type": "string"} for c in [
                                "event_id", "vehicle_id", "vin", "timestamp", "battery_level",
                                "speed", "temperature", "latitude", "longitude",
                                "quarantine_dataset", "quarantine_error_type",
                                "quarantine_error_message", "quarantine_validation_rule",
                                "quarantine_timestamp",
                            ]
                        ],
                    },
                },
            )
        except Exception:
            pass

    # ── data_quality_report: repoint at the flat JSON summary prefix ──
    try:
        resp = glue.get_table(DatabaseName=GLUE_DATABASE, Name="data_quality_report")
        table = resp["Table"]
        sd = table.get("StorageDescriptor", {})
        desired_location = f"s3://{S3_BUCKET}/{REPORT_PREFIX}/summary/"
        if sd.get("Location") != desired_location:
            sd["Location"] = desired_location
            glue.update_table(
                DatabaseName=GLUE_DATABASE,
                TableInput={
                    "Name": table["Name"],
                    "TableType": table.get("TableType", "EXTERNAL_TABLE"),
                    "Parameters": table.get("Parameters", {}),
                    "StorageDescriptor": sd,
                },
            )
    except Exception:
        pass


def _run_athena_query(athena, sql: str) -> dict:
    """Execute a SQL query on real AWS Athena and return columns/rows/duration."""
    start_time = time.time()
    resp = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": GLUE_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT_LOCATION},
        WorkGroup=ATHENA_WORKGROUP,
    )
    query_id = resp["QueryExecutionId"]

    state = "RUNNING"
    status = {}
    while state in ("RUNNING", "QUEUED"):
        status = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]["Status"]
        state = status["State"]
        if state in ("RUNNING", "QUEUED"):
            time.sleep(0.4)

    if state != "SUCCEEDED":
        reason = status.get("StateChangeReason", f"Athena query ended with state {state}")
        raise RuntimeError(reason)

    columns: list[str] = []
    rows: list[dict] = []
    paginator = athena.get_paginator("get_query_results")
    first_page = True
    for page in paginator.paginate(QueryExecutionId=query_id):
        result_set = page["ResultSet"]
        if first_page:
            columns = [c["Label"] for c in result_set["ResultSetMetadata"]["ColumnInfo"]]
        for i, row in enumerate(result_set["Rows"]):
            if first_page and i == 0:
                continue  # header row
            values = [d.get("VarCharValue", "") for d in row["Data"]]
            rows.append(dict(zip(columns, values)))
        first_page = False

    duration = f"{time.time() - start_time:.3f}s"
    return {
        "columns": columns,
        "rows": rows,
        "rowCount": len(rows),
        "duration": duration,
        "database": GLUE_DATABASE,
        "region": AWS_REGION,
    }



# ────────────────────────────────────────────────────────────────────
# Run history (local index of every uploaded/processed file)
# ────────────────────────────────────────────────────────────────────

HISTORY_PATH = PROJECT_ROOT / "output" / "history.json"


def _load_history() -> list[dict]:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except Exception:
            return []
    return []
# ────────────────────────────────────────────────────────────────────
# Run history — stored in S3 as the single source of truth.
# Falls back to a local file only when AWS/S3 is unreachable.
# ────────────────────────────────────────────────────────────────────

HISTORY_PATH = PROJECT_ROOT / "output" / "history.json"  # offline fallback only
HISTORY_KEY = f"{REPORT_PREFIX}/_history.json"


def _load_history(s3=None) -> list[dict]:
    s3 = s3 if s3 is not None else _get_s3()
    if s3:
        data = _get_s3_json(s3, HISTORY_KEY)
        if data is not None:
            return data
        return []
    # Offline fallback
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except Exception:
            return []
    return []


def _save_history(history: list[dict], s3=None) -> None:
    s3 = s3 if s3 is not None else _get_s3()
    if s3:
        try:
            _upload_json_to_s3(s3, history, HISTORY_KEY)
            return
        except Exception:
            pass
    # Offline fallback
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2, default=str))


def _add_history_entry(entry: dict, s3=None) -> None:
    s3 = s3 if s3 is not None else _get_s3()
    history = _load_history(s3)
    history.append(entry)
    # Keep the most recent 200 runs
    history = history[-200:]
    _save_history(history, s3)


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
    """Load the most recent vehicle_master CSV from S3 raw/, falling back to the local sample."""
    if s3:
        try:
            resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{RAW_PREFIX}/vehicle_master/")
            objects = sorted(resp.get("Contents", []), key=lambda o: o["LastModified"], reverse=True)
            csv_objects = [o for o in objects if o["Key"].endswith(".csv")]
            if csv_objects:
                df = _get_s3_csv(s3, csv_objects[0]["Key"])
                if df is not None:
                    return df
        except Exception:
            pass

    # Offline fallback — only used when AWS is unreachable
    local_path = PROJECT_ROOT / "data" / "sample" / "bmw_vehicle_master.csv"
    if local_path.exists():
        return pd.read_csv(local_path)
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
    run_id = f"{ts}_{dataset}"
    logger = BmwLogger(dataset)

    # ── 1. Load vehicle master for referential integrity ───────
    reference_pdf = _load_vehicle_master(s3)

    # ── 2. Quality engine (PySpark) ─────────────────────────────
    spark = get_spark()
    spark_df = spark.createDataFrame(df)
    reference_df = spark.createDataFrame(reference_pdf) if reference_pdf is not None else None

    engine = QualityEngine(dataset=dataset, logger=logger)
    valid_spark_df, invalid_spark_df, metrics = engine.run(spark_df, reference_df=reference_df)

    # ── 3. Quality score ───────────────────────────────────────
    scorer = QualityScoreCalculator()
    scorer.apply_to_metrics(metrics)

    # ── 4. Quality report ──────────────────────────────────────
    reporter = QualityReporter(calculator=scorer)
    text_report, json_report = reporter.generate(metrics)

    # ── 5. Quarantine (PySpark) ──────────────────────────────────
    qm = QuarantineManager(dataset=dataset, logger=logger)
    quarantine_spark_df = qm.prepare(invalid_spark_df)

    # Materialise to pandas — everything past this point (S3 upload,
    # history, JSON responses) operates on pandas as before.
    valid_df = valid_spark_df.toPandas()
    quarantine_df = quarantine_spark_df.toPandas()

    # ── 6. Save outputs — S3 is the single source of truth ─────
    s3_paths: dict[str, str] = {}
    storage_mode = "s3" if s3 else "local"
    keys: dict[str, Optional[str]] = {
        "curated_key": None, "quarantine_key": None,
        "report_json_key": None, "report_txt_key": None,
        "summary_key": None, "log_key": None,
    }
    local_paths: dict[str, Optional[str]] = {
        "local_quarantine_path": None, "local_curated_path": None,
        "local_report_json_path": None, "local_report_txt_path": None,
        "local_log_path": None,
    }

    if s3:
        # Upload curated
        curated_key = f"{CURATED_PREFIX}/{dataset}/{run_id}_curated.csv"
        s3_paths["curated"] = _upload_df_to_s3(s3, valid_df, curated_key)
        keys["curated_key"] = curated_key

        # Upload quarantine
        if len(quarantine_df) > 0:
            quarantine_key = f"{QUARANTINE_PREFIX}/{dataset}/{run_id}_quarantine.csv"
            s3_paths["quarantine"] = _upload_df_to_s3(s3, quarantine_df, quarantine_key)
            keys["quarantine_key"] = quarantine_key

        # Upload JSON report
        report_key = f"{REPORT_PREFIX}/{dataset}/{run_id}_quality_report.json"
        s3_paths["report"] = _upload_json_to_s3(s3, json_report, report_key)
        keys["report_json_key"] = report_key

        # Upload text report
        txt_key = f"{REPORT_PREFIX}/{dataset}/{run_id}_quality_report.txt"
        s3.put_object(Bucket=S3_BUCKET, Key=txt_key, Body=text_report.encode(), ContentType="text/plain")
        keys["report_txt_key"] = txt_key

        # Upload flat JSON summary — backs the Glue `data_quality_report` table
        summary_key = f"{REPORT_PREFIX}/summary/{run_id}.json"
        summary_row = {
            "dataset_name": dataset,
            "execution_timestamp": metrics.execution_time,
            "total_records": metrics.total_records,
            "valid_records": metrics.valid_records,
            "rejected_records": metrics.rejected_records,
            "quality_score": metrics.quality_score,
            "null_issues": metrics.null_count,
            "duplicate_records": metrics.duplicate_count,
            "invalid_vin_count": metrics.invalid_vin_count,
            "invalid_date_count": metrics.invalid_date_count,
            "range_violation_count": metrics.range_violation_count,
            "referential_errors": metrics.referential_error_count,
        }
        _upload_json_to_s3(s3, summary_row, summary_key)
        keys["summary_key"] = summary_key
    else:
        # Offline fallback — only used when AWS is unreachable
        local_base = PROJECT_ROOT / "output"
        for subdir in ["curated", "quarantine", "reports", "logs"]:
            (local_base / subdir).mkdir(parents=True, exist_ok=True)

        local_curated_path = local_base / "curated" / f"{run_id}_curated.csv"
        valid_df.to_csv(local_curated_path, index=False)
        local_paths["local_curated_path"] = str(local_curated_path)
        s3_paths["curated"] = str(local_curated_path)

        if len(quarantine_df) > 0:
            local_quarantine_path = local_base / "quarantine" / f"{run_id}_quarantine.csv"
            quarantine_df.to_csv(local_quarantine_path, index=False)
            local_paths["local_quarantine_path"] = str(local_quarantine_path)
            s3_paths["quarantine"] = str(local_quarantine_path)

        local_report_json_path = local_base / "reports" / f"{run_id}_quality_report.json"
        local_report_json_path.write_text(json.dumps(json_report, indent=2, default=str))
        local_paths["local_report_json_path"] = str(local_report_json_path)
        s3_paths["report"] = str(local_report_json_path)

        local_txt_path = local_base / "reports" / f"{run_id}_quality_report.txt"
        local_txt_path.write_text(text_report)
        local_paths["local_report_txt_path"] = str(local_txt_path)

    # ── 7. CloudWatch logging ──────────────────────────────────
    captured_logs = logger.get_logs()
    try:
        from src.monitoring.cloudwatch_logger import CloudWatchLogger
        cw = CloudWatchLogger(dataset=dataset, logger=logger)
        logger.pipeline_end()
        captured_logs = logger.get_logs()
        cw.upload_logs(captured_logs)
        cw.put_metric("QualityScore", metrics.quality_score, "None")
        cw.put_metric("RejectedRecords", metrics.rejected_records, "Count")
        cw.put_metric("ValidRecords", metrics.valid_records, "Count")
    except Exception:
        pass  # CloudWatch is optional — don't fail the whole request

    # Persist logs — S3 when connected, local file only as offline fallback
    if s3:
        log_key = f"{LOG_PREFIX}/{dataset}/{run_id}_logs.json"
        _upload_json_to_s3(s3, captured_logs, log_key)
        keys["log_key"] = log_key
    else:
        local_log_path = local_base / "logs" / f"{run_id}_logs.json"
        local_log_path.write_text(json.dumps(captured_logs, indent=2, default=str))
        local_paths["local_log_path"] = str(local_log_path)

    raw_s3_path = f"s3://{S3_BUCKET}/{RAW_PREFIX}/{dataset}/{filename}" if s3 else None

    result = {
        **json_report,
        "run_id": run_id,
        "filename": filename,
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
        "raw_s3_path": raw_s3_path,
        "execution_time": metrics.execution_time,
        "duration_seconds": metrics.duration_seconds,
        "quarantine_records": (
            quarantine_df.head(1000).fillna("").to_dict(orient="records")
            if len(quarantine_df) > 0 else []
        ),
        "logs": captured_logs,
    }

    # ── 8. Record history entry ─────────────────────────────────
    _add_history_entry({
        "run_id": run_id,
        "filename": filename,
        "dataset": dataset,
        "timestamp": metrics.execution_time,
        "total_records": metrics.total_records,
        "valid_records": metrics.valid_records,
        "rejected_records": metrics.rejected_records,
        "quality_score": metrics.quality_score,
        "score_label": metrics.score_label,
        "aws_connected": s3 is not None,
        "storage": storage_mode,
        "s3_paths": s3_paths,
        **keys,
        **local_paths,
    }, s3)

    return result


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
async def upload_csv(file: UploadFile = File(...), dataset: Optional[str] = Form(None)):
    """
    Main endpoint — accepts a BMW CSV file, runs the quality pipeline,
    and returns the full quality report JSON.

    The caller chooses which dataset the file belongs to ('telemetry' or
    'vehicle_master') via the `dataset` form field. If omitted, the dataset
    is auto-detected from the CSV columns.

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

    # Determine dataset type — prefer the user's explicit selection
    if dataset in ("telemetry", "vehicle_master"):
        resolved_dataset = dataset
    else:
        resolved_dataset = detect_dataset(list(df.columns))
        if resolved_dataset == "unknown":
            raise HTTPException(
                status_code=400,
                detail="Could not detect dataset type. Please select 'telemetry' or 'vehicle_master'.",
            )

    # Try to get S3 client (non-blocking — falls back to local)
    s3 = _get_s3()

    # Upload raw CSV to S3
    if s3:
        raw_key = f"{RAW_PREFIX}/{resolved_dataset}/{file.filename}"
        try:
            _upload_bytes_to_s3(s3, raw_bytes, raw_key)
        except Exception:
            s3 = None  # Fallback to local if upload fails

    # Run the quality pipeline
    try:
        report = run_pipeline_on_df(
            df=df,
            dataset=resolved_dataset,
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


# ────────────────────────────────────────────────────────────────────
# History — list & inspect every processed CSV file
# ────────────────────────────────────────────────────────────────────

@app.get("/api/history")
async def list_history(dataset: Optional[str] = None):
    """Return all processed files (most recent first), optionally filtered by dataset."""
    history = _load_history()
    if dataset and dataset != "ALL":
        history = [h for h in history if h.get("dataset") == dataset]
    history = sorted(history, key=lambda h: h.get("timestamp", ""), reverse=True)
    return JSONResponse(content={"runs": history, "total": len(history)})


def _find_history_entry(run_id: str) -> Optional[dict]:
    history = _load_history()
    for h in history:
        if h.get("run_id") == run_id:
            return h
    return None


@app.get("/api/history/{run_id}")
async def get_history_entry(run_id: str):
    """Return the full quality report + logs for one specific processed file."""
    entry = _find_history_entry(run_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"No run found with id '{run_id}'")

    s3 = _get_s3() if entry.get("storage") == "s3" else None

    data: dict = {}
    text_report = ""
    logs: list = []

    if s3:
        if entry.get("report_json_key"):
            data = _get_s3_json(s3, entry["report_json_key"]) or {}
        if entry.get("report_txt_key"):
            text_report = _get_s3_text(s3, entry["report_txt_key"]) or ""
        if entry.get("log_key"):
            logs = _get_s3_json(s3, entry["log_key"]) or []
    else:
        report_path = entry.get("local_report_json_path")
        if report_path and Path(report_path).exists():
            data = json.loads(Path(report_path).read_text())
        txt_path = entry.get("local_report_txt_path")
        if txt_path and Path(txt_path).exists():
            text_report = Path(txt_path).read_text()
        log_path = entry.get("local_log_path")
        if log_path and Path(log_path).exists():
            logs = json.loads(Path(log_path).read_text())

    rep = data.get("bmw_data_quality_report", {})
    rec = rep.get("record_summary", {})
    chk = rep.get("quality_checks", {})

    return JSONResponse(content={
        **data,
        "run_id": entry["run_id"],
        "filename": entry.get("filename"),
        "dataset": entry.get("dataset"),
        "execution_time": entry.get("timestamp"),
        "quality_score": entry.get("quality_score"),
        "score_label": entry.get("score_label"),
        "total_records": entry.get("total_records") or rec.get("total_records", 0),
        "valid_records": entry.get("valid_records") or rec.get("valid_records", 0),
        "rejected_records": entry.get("rejected_records") or rec.get("rejected_records", 0),
        "null_count": chk.get("null_issues", 0),
        "duplicate_count": chk.get("duplicate_records", 0),
        "invalid_vin_count": chk.get("invalid_vin", 0),
        "invalid_date_count": chk.get("invalid_dates", 0),
        "range_violation_count": chk.get("range_violations", 0),
        "referential_error_count": chk.get("referential_errors", 0),
        "null_summary": rep.get("null_analysis", []),
        "penalty_breakdown": rep.get("penalty_breakdown", {}),
        "s3_paths": entry.get("s3_paths", {}),
        "aws_connected": entry.get("aws_connected", False),
        "text_report": text_report,
        "duration_seconds": rep.get("duration_seconds", 0),
        "logs": logs,
    })


# ────────────────────────────────────────────────────────────────────
# Quarantine — real records from a specific run (or the latest one)
# ────────────────────────────────────────────────────────────────────

def _resolve_quarantine_df(run_id: Optional[str], dataset: str) -> tuple[Optional[pd.DataFrame], Optional[dict]]:
    history = _load_history()
    if run_id:
        entry = next((h for h in history if h.get("run_id") == run_id), None)
    else:
        matching = [h for h in history if h.get("dataset") == dataset]
        entry = matching[-1] if matching else None

    if not entry:
        return None, None

    if entry.get("storage") == "s3" and entry.get("quarantine_key"):
        s3 = _get_s3()
        if s3:
            df = _get_s3_csv(s3, entry["quarantine_key"])
            if df is not None:
                return df, entry
        return pd.DataFrame(), entry

    q_path = entry.get("local_quarantine_path")
    if q_path and Path(q_path).exists():
        return pd.read_csv(Path(q_path)), entry
    return pd.DataFrame(), entry


@app.get("/api/quarantine")
async def get_quarantine_records(
    dataset: str = "telemetry",
    run_id: Optional[str] = None,
    error_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """Return real quarantine records for a dataset or a specific processed file (run_id)."""
    df, entry = _resolve_quarantine_df(run_id, dataset)
    if df is None:
        return JSONResponse(content={"total": 0, "records": [], "error_counts": {}, "run_id": run_id})

    full_df = df.copy()

    if error_type and error_type != "ALL":
        if "quarantine_error_type" in df.columns:
            df = df[df["quarantine_error_type"].astype(str).str.contains(error_type, na=False)]

    if search:
        s = search.lower()
        if len(df) > 0:
            mask = df.astype(str).apply(lambda row: row.str.lower().str.contains(s).any(), axis=1)
            df = df[mask]

    error_counts: dict[str, int] = {}
    if "quarantine_error_type" in full_df.columns:
        for val in full_df["quarantine_error_type"].dropna():
            for t in str(val).split("|"):
                t = t.strip()
                if t:
                    error_counts[t] = error_counts.get(t, 0) + 1

    total_matched = len(df)
    records = df.iloc[offset: offset + limit].fillna("").to_dict(orient="records")

    return JSONResponse(content={
        "total": total_matched,
        "records": records,
        "error_counts": error_counts,
        "dataset": dataset,
        "run_id": entry.get("run_id") if entry else None,
    })


# ────────────────────────────────────────────────────────────────────
# Logs — pipeline execution logs for a specific run
# ────────────────────────────────────────────────────────────────────

@app.get("/api/logs")
async def get_pipeline_logs(run_id: Optional[str] = None, dataset: str = "telemetry"):
    """Return real pipeline logs for a specific run, or the latest run for a dataset."""
    history = _load_history()
    if run_id:
        entry = next((h for h in history if h.get("run_id") == run_id), None)
    else:
        matching = [h for h in history if h.get("dataset") == dataset]
        entry = matching[-1] if matching else None

    if not entry:
        return JSONResponse(content={"logs": [], "run_id": None})

    logs = []
    if entry.get("storage") == "s3" and entry.get("log_key"):
        s3 = _get_s3()
        if s3:
            logs = _get_s3_json(s3, entry["log_key"]) or []
    else:
        log_path = entry.get("local_log_path")
        if log_path and Path(log_path).exists():
            logs = json.loads(Path(log_path).read_text())

    return JSONResponse(content={"logs": logs, "run_id": entry.get("run_id")})


# ────────────────────────────────────────────────────────────────────
# Athena — real AWS Athena execution against the Glue Data Catalog.
# Falls back to a local SQLite emulation only when AWS is unreachable.
# ────────────────────────────────────────────────────────────────────

def _execute_athena_query_local(sql: str) -> dict:
    """Offline fallback: emulate Athena with SQLite over the last locally-saved files."""
    import sqlite3
    import re

    start_time = time.time()
    conn = sqlite3.connect(":memory:")
    try:
        history = _load_history()

        vm_entries = [h for h in history if h.get("dataset") == "vehicle_master"]
        vm_path = Path(vm_entries[-1]["local_curated_path"]) if vm_entries and vm_entries[-1].get("local_curated_path") else (
            PROJECT_ROOT / "data" / "sample" / "bmw_vehicle_master.csv"
        )
        if vm_path.exists():
            pd.read_csv(vm_path).to_sql("vehicle_master", conn, index=False, if_exists="replace")

        t_entries = [h for h in history if h.get("dataset") == "telemetry"]
        t_path = Path(t_entries[-1]["local_curated_path"]) if t_entries and t_entries[-1].get("local_curated_path") else (
            PROJECT_ROOT / "data" / "sample" / "bmw_telemetry.csv"
        )
        if t_path.exists():
            pd.read_csv(t_path).to_sql("telemetry", conn, index=False, if_exists="replace")

        q_entries = [h for h in t_entries if h.get("local_quarantine_path")]
        if q_entries:
            q_path = Path(q_entries[-1]["local_quarantine_path"])
            if q_path.exists():
                pd.read_csv(q_path).to_sql("quarantine_telemetry", conn, index=False, if_exists="replace")

        if history:
            report_rows = [{
                "dataset_name": h.get("dataset"),
                "execution_timestamp": h.get("timestamp"),
                "total_records": h.get("total_records", 0),
                "valid_records": h.get("valid_records", 0),
                "rejected_records": h.get("rejected_records", 0),
                "quality_score": h.get("quality_score", 0),
                "score_label": h.get("score_label", ""),
            } for h in history]
            pd.DataFrame(report_rows).to_sql("data_quality_report", conn, index=False, if_exists="replace")

        cleaned_sql = re.sub(r'bmw_data_quality\.', '', sql, flags=re.IGNORECASE)
        cleaned_sql = re.sub(r'CAST\((.*?)\s+AS\s+DOUBLE\)', r'CAST(\1 AS REAL)', cleaned_sql, flags=re.IGNORECASE)

        result_df = pd.read_sql_query(cleaned_sql, conn)
        duration = f"{time.time() - start_time:.3f}s"

        return {
            "columns": list(result_df.columns),
            "rows": result_df.fillna("").to_dict(orient="records"),
            "rowCount": len(result_df),
            "duration": duration,
            "database": "bmw_data_quality (offline emulation)",
            "region": AWS_REGION,
        }
    finally:
        conn.close()


@app.post("/api/athena/query")
async def execute_athena_query(payload: dict):
    """
    Execute a SQL query.

    When AWS is reachable, this runs the query on real Amazon Athena against
    the live Glue Data Catalog (bmw_data_quality database) and reads results
    back from the Athena output location in S3. Only falls back to a local
    SQLite emulation when AWS/S3 is unreachable (offline development).
    """
    sql = (payload or {}).get("sql", "").strip()
    if not sql:
        raise HTTPException(status_code=400, detail="SQL query is required")

    s3 = _get_s3()
    if s3:
        glue = _get_glue()
        athena = _get_athena()
        if athena:
            try:
                _ensure_glue_tables(glue)
                return JSONResponse(content=_run_athena_query(athena, sql))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Athena query failed: {e}")

    # Offline fallback — AWS unreachable
    try:
        return JSONResponse(content=_execute_athena_query_local(sql))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ────────────────────────────────────────────────────────────────────
# Governance — real S3 zones, role permissions, and Lake Formation policies
# ────────────────────────────────────────────────────────────────────

@app.get("/api/governance")
async def get_governance_info():
    """Return governance zones, role permissions, and resource policies for the live bucket."""
    s3 = _get_s3()
    return JSONResponse(content={
        "s3_bucket": S3_BUCKET,
        "region": AWS_REGION,
        "aws_connected": s3 is not None,
        "zones": [
            {"id": "raw", "name": "Raw", "desc": "Original unmodified BMW datasets", "path": f"s3://{S3_BUCKET}/{RAW_PREFIX}/"},
            {"id": "curated", "name": "Curated", "desc": "Validated records ready for analytics", "path": f"s3://{S3_BUCKET}/{CURATED_PREFIX}/"},
            {"id": "quarantine", "name": "Quarantine", "desc": "Invalid records for investigation", "path": f"s3://{S3_BUCKET}/{QUARANTINE_PREFIX}/"},
            {"id": "reports", "name": "Reports", "desc": "Quality reports and scoring outputs", "path": f"s3://{S3_BUCKET}/{REPORT_PREFIX}/"},
        ],
        "roles": [
            {"role": "Data Engineer", "desc": "Full pipeline access — can read raw data, curated data, quarantine, and quality reports.", "zones": {"raw": True, "curated": True, "quarantine": True, "reports": True}},
            {"role": "Data Analyst", "desc": "Analytics access — can query curated data and review quality reports via Athena.", "zones": {"raw": False, "curated": True, "quarantine": False, "reports": True}},
            {"role": "Business User", "desc": "Report-only access — can view approved quality reports and dashboard summaries.", "zones": {"raw": False, "curated": False, "quarantine": False, "reports": True}},
        ],
        "policies": [
            {"id": "P01", "resource": f"s3://{S3_BUCKET}/raw/", "action": "lakeformation:DescribeResource", "principal": "data-engineers", "effect": "Allow"},
            {"id": "P02", "resource": f"s3://{S3_BUCKET}/curated/", "action": "lakeformation:DescribeResource", "principal": "data-engineers, data-analysts", "effect": "Allow"},
            {"id": "P03", "resource": f"s3://{S3_BUCKET}/quarantine/", "action": "lakeformation:DescribeResource", "principal": "data-engineers", "effect": "Allow"},
            {"id": "P04", "resource": f"s3://{S3_BUCKET}/reports/", "action": "lakeformation:DescribeResource", "principal": "all", "effect": "Allow"},
            {"id": "P05", "resource": f"s3://{S3_BUCKET}/raw/", "action": "lakeformation:DescribeResource", "principal": "business-users", "effect": "Deny"},
        ],
    })
