"""
BMW Data Quality & Governance Platform — Main Entry Point
Participant 12 | Pod D

Usage (local):
    python src/main.py --dataset telemetry --input data/sample/bmw_telemetry_demo.csv --local

Usage (S3):
    python src/main.py --dataset telemetry --s3-key raw/telemetry/bmw_telemetry.csv
"""

import argparse
import sys
import json
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import S3_BUCKET, CURATED_PREFIX, QUARANTINE_PREFIX, REPORT_PREFIX
from src.utils.logger import BmwLogger
from src.ingestion.s3_loader import S3Loader
from src.processing.quality_engine import QualityEngine
from src.processing.quarantine import QuarantineManager
from src.scoring.quality_score import QualityScoreCalculator
from src.reporting.quality_report import QualityReporter
from src.monitoring.cloudwatch_logger import CloudWatchLogger


def run_pipeline(
    dataset: str,
    input_path: str | None = None,
    s3_key: str | None = None,
    vehicle_master_path: str | None = None,
    local_output: str | None = None,
    local: bool = True,
) -> dict:
    """
    Execute the full BMW Data Quality pipeline.

    Returns the JSON quality report dict.
    """
    logger = BmwLogger(dataset)
    loader = S3Loader(bucket=S3_BUCKET, logger=logger)
    cw = CloudWatchLogger(dataset=dataset, logger=logger)

    try:
        # ── 1. Load raw dataset ───────────────────────────────
        df = loader.load_csv(key=s3_key or "", local_path=input_path)
        logger.info(f"Loaded {len(df):,} rows from {'local' if input_path else 'S3'}")

        # ── 2. Load vehicle master (for referential integrity) ─
        vm_path = vehicle_master_path or "data/sample/bmw_vehicle_master.csv"
        reference_df = None
        if Path(vm_path).exists():
            reference_df = loader.load_csv(key="raw/vehicle_master/vehicle_master.csv", local_path=vm_path)
            logger.info(f"Vehicle master loaded: {len(reference_df):,} rows")

        # ── 3. Run quality engine ─────────────────────────────
        engine = QualityEngine(dataset=dataset, logger=logger)
        valid_df, invalid_df, metrics = engine.run(df, reference_df=reference_df)

        # ── 4. Calculate quality score ────────────────────────
        scorer = QualityScoreCalculator()
        scorer.apply_to_metrics(metrics)
        logger.quality_score(metrics.quality_score)

        # ── 5. Generate quality report ────────────────────────
        reporter = QualityReporter(calculator=scorer)
        text_report, json_report = reporter.generate(metrics)
        print(text_report)

        # ── 6. Quarantine invalid records ─────────────────────
        qm = QuarantineManager(dataset=dataset, logger=logger)
        quarantine_df = qm.prepare(invalid_df)
        out_dir = local_output or "output/quarantine"
        qm.save(quarantine_df, out_dir)

        # ── 7. Save curated records ───────────────────────────
        curated_dir = local_output.replace("quarantine", "curated") if local_output else "output/curated"
        if local:
            Path(curated_dir).mkdir(parents=True, exist_ok=True)
            curated_file = Path(curated_dir) / f"{dataset}_curated.csv"
            valid_df.to_csv(curated_file, index=False)
            logger.info(f"Curated data saved: {curated_file}")

        # ── 8. Save report ────────────────────────────────────
        report_dir = local_output.replace("quarantine", "reports") if local_output else "output/reports"
        if local:
            Path(report_dir).mkdir(parents=True, exist_ok=True)
            report_json_file = Path(report_dir) / f"{dataset}_quality_report.json"
            report_txt_file = Path(report_dir) / f"{dataset}_quality_report.txt"
            report_json_file.write_text(json.dumps(json_report, indent=2, default=str))
            report_txt_file.write_text(text_report)
            logger.info(f"Reports saved: {report_dir}/")

        # ── 9. CloudWatch ─────────────────────────────────────
        logger.pipeline_end()
        cw.upload_logs(logger.get_logs())
        cw.put_metric("QualityScore", metrics.quality_score, "None")
        cw.put_metric("RejectedRecords", metrics.rejected_records, "Count")
        cw.put_metric("ValidRecords", metrics.valid_records, "Count")

        return json_report

    except Exception as exc:
        logger.error(f"Pipeline failed: {exc}")
        cw.upload_logs(logger.get_logs())
        raise


def main():
    parser = argparse.ArgumentParser(
        description="BMW Data Quality & Governance Platform"
    )
    parser.add_argument("--dataset", required=True, help="Dataset name (e.g. telemetry)")
    parser.add_argument("--input", help="Local CSV file path")
    parser.add_argument("--s3-key", help="S3 object key for input file")
    parser.add_argument("--vehicle-master", help="Path to vehicle_master.csv")
    parser.add_argument("--output", default="output", help="Local output base directory")
    parser.add_argument("--local", action="store_true", default=True, help="Use local filesystem")
    args = parser.parse_args()

    run_pipeline(
        dataset=args.dataset,
        input_path=args.input,
        s3_key=args.s3_key,
        vehicle_master_path=args.vehicle_master,
        local_output=f"{args.output}/quarantine",
        local=args.local,
    )


if __name__ == "__main__":
    main()
