"""
BMW Data Quality & Governance Platform — Logger
Participant 12 | Pod D
Structured logger that emits CloudWatch-compatible log lines.
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Optional


class BmwLogger:
    """
    Structured logger producing CloudWatch-compatible output.
    Format: [LEVEL] [timestamp] [dataset] message
    """

    def __init__(self, dataset: str = "general", log_file: Optional[str] = None):
        self.dataset = dataset
        self._logs: list[dict] = []

        self._logger = logging.getLogger(f"bmw.{dataset}")
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter("[%(levelname)s] %(message)s")
            )
            self._logger.addHandler(handler)

            if log_file:
                fh = logging.FileHandler(log_file)
                fh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
                self._logger.addHandler(fh)

    def _record(self, level: str, message: str) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "dataset": self.dataset,
            "message": message,
        }
        self._logs.append(entry)
        return entry

    def info(self, message: str) -> None:
        self._record("INFO", message)
        self._logger.info(f"[{self.dataset}] {message}")

    def warn(self, message: str) -> None:
        self._record("WARN", message)
        self._logger.warning(f"[{self.dataset}] {message}")

    def error(self, message: str) -> None:
        self._record("ERROR", message)
        self._logger.error(f"[{self.dataset}] {message}")

    def get_logs(self) -> list[dict]:
        """Return all captured log entries (for CloudWatch upload)."""
        return list(self._logs)

    def pipeline_start(self) -> None:
        self.info("Pipeline started")

    def pipeline_end(self) -> None:
        self.info("Pipeline completed")

    def records_received(self, count: int) -> None:
        self.info(f"Records received: {count:,}")

    def records_processed(self, count: int) -> None:
        self.info(f"Records processed: {count:,}")

    def valid_records(self, count: int) -> None:
        self.info(f"Valid records: {count:,}")

    def rejected_records(self, count: int) -> None:
        self.warn(f"Rejected records: {count:,}")

    def quality_score(self, score: float) -> None:
        self.info(f"Quality score: {score:.1f}")
