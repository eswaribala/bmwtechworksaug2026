"""
BMW Data Quality & Governance Platform — CloudWatch Logger
Participant 12 | Pod D
Uploads log events to AWS CloudWatch Logs; falls back to stdout gracefully.
"""

import json
import time
from datetime import datetime, timezone
from typing import Optional
from src.utils.config import CLOUDWATCH_LOG_GROUP, CLOUDWATCH_LOG_STREAM_PREFIX
from src.utils.logger import BmwLogger


class CloudWatchLogger:
    """
    Sends log events to Amazon CloudWatch Logs.
    When boto3 / credentials are unavailable, silently falls back to stdout.
    """

    def __init__(
        self,
        dataset: str,
        log_group: str = CLOUDWATCH_LOG_GROUP,
        logger: Optional[BmwLogger] = None,
    ):
        self.dataset = dataset
        self.log_group = log_group
        self.log_stream = f"{CLOUDWATCH_LOG_STREAM_PREFIX}-{dataset}-{self._ts_str()}"
        self.logger = logger or BmwLogger(dataset)
        self._client = None
        self._sequence_token: Optional[str] = None
        self._available = self._init_client()

    # ──────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────

    def upload_logs(self, log_entries: list[dict]) -> bool:
        """
        Upload a list of log entries (from BmwLogger.get_logs()) to CloudWatch.

        Returns True if successful, False if CloudWatch is unavailable.
        """
        if not self._available or not log_entries:
            return False

        events = [
            {
                "timestamp": int(
                    datetime.fromisoformat(e["timestamp"]).timestamp() * 1000
                ),
                "message": json.dumps(e, default=str),
            }
            for e in log_entries
        ]
        # Sort by timestamp (required by CloudWatch)
        events.sort(key=lambda x: x["timestamp"])

        try:
            kwargs = {
                "logGroupName": self.log_group,
                "logStreamName": self.log_stream,
                "logEvents": events,
            }
            if self._sequence_token:
                kwargs["sequenceToken"] = self._sequence_token

            response = self._client.put_log_events(**kwargs)
            self._sequence_token = response.get("nextSequenceToken")
            self.logger.info(f"CloudWatch: uploaded {len(events)} log events")
            return True

        except Exception as exc:
            self.logger.warn(f"CloudWatch upload failed: {exc}")
            return False

    def put_metric(self, metric_name: str, value: float, unit: str = "Count") -> bool:
        """
        Publish a single metric to CloudWatch Metrics.
        Namespace: 'BMW/DataQuality'
        """
        if not self._available:
            return False
        try:
            import boto3
            cw = boto3.client("cloudwatch")
            cw.put_metric_data(
                Namespace="BMW/DataQuality",
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Dimensions": [{"Name": "Dataset", "Value": self.dataset}],
                        "Value": value,
                        "Unit": unit,
                        "Timestamp": datetime.now(timezone.utc),
                    }
                ],
            )
            return True
        except Exception as exc:
            self.logger.warn(f"CloudWatch metric failed: {exc}")
            return False

    # ──────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────

    def _init_client(self) -> bool:
        try:
            import boto3
            self._client = boto3.client("logs")
            # Try to create log group and stream (idempotent)
            try:
                self._client.create_log_group(logGroupName=self.log_group)
            except self._client.exceptions.ResourceAlreadyExistsException:
                pass
            try:
                self._client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream,
                )
            except self._client.exceptions.ResourceAlreadyExistsException:
                pass
            self.logger.info(f"CloudWatch connected: {self.log_group}/{self.log_stream}")
            return True
        except Exception:
            self.logger.warn("CloudWatch not available — falling back to stdout only")
            return False

    @staticmethod
    def _ts_str() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
