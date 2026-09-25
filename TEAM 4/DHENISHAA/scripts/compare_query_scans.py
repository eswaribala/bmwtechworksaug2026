"""Compare Athena scan sizes between a broad query and a partition-aware query."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import boto3


def summarize_execution(result: dict[str, Any]) -> dict[str, Any]:
    """Extract core Athena execution metrics for a query run."""
    execution = result["QueryExecution"]
    status = execution["Status"]
    stats = execution.get("Statistics", {})
    return {
        "query_execution_id": execution["QueryExecutionId"],
        "state": status["State"],
        "data_scanned_in_bytes": stats.get("DataScannedInBytes"),
        "query": execution.get("Statement"),
        "result_location": execution.get("ResultConfiguration", {}).get("OutputLocation"),
    }


def wait_for_query(client, execution_id: str) -> dict[str, Any]:
    """Wait until the Athena query reaches a terminal state."""
    while True:
        result = client.get_query_execution(QueryExecutionId=execution_id)
        state = result["QueryExecution"]["Status"]["State"]
        if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            return result
        time.sleep(2)


def run_query(client, query: str, database: str, workgroup: str, output_location: str | None = None) -> dict[str, Any]:
    """Submit a query to Athena and return detailed execution data."""
    request = {
        "QueryString": query,
        "QueryExecutionContext": {"Database": database},
        "WorkGroup": workgroup,
    }
    if output_location:
        request["ResultConfiguration"] = {"OutputLocation": output_location}

    response = client.start_query_execution(**request)
    result = wait_for_query(client, response["QueryExecutionId"])
    return result


def build_report(output_path: str | Path, broad_result: dict[str, Any], partitioned_result: dict[str, Any]) -> str:
    """Create a Markdown report comparing broad vs partition-aware Athena scans."""
    broad_bytes = broad_result["QueryExecution"].get("Statistics", {}).get("DataScannedInBytes", 0)
    partitioned_bytes = partitioned_result["QueryExecution"].get("Statistics", {}).get("DataScannedInBytes", 0)

    reduction = None
    if broad_bytes:
        reduction = (1 - (partitioned_bytes / broad_bytes)) * 100

    report = f"""# Athena Query Scan Comparison

## Summary
This report compares the cost of scanning the telemetry dataset before and after a partition-aware filter.

## Measurements
- unpartitioned_scan_bytes: {broad_bytes}
- partitioned_scan_bytes: {partitioned_bytes}
- reduction_percent: {reduction if reduction is not None else 'N/A'}

## Detailed query execution
### Broad scan
{json.dumps(summarize_execution(broad_result), indent=2, default=str)}

### Partition-aware scan
{json.dumps(summarize_execution(partitioned_result), indent=2, default=str)}

## Notes
- Values are captured from real Athena executions and should not be fabricated.
- Use partition filters such as `year` and `month` to lower scan volume.
"""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Athena scan comparison report from real query execution metrics.")
    parser.add_argument("--database", required=True, help="Glue catalog database name.")
    parser.add_argument("--workgroup", default="primary", help="Athena workgroup name.")
    parser.add_argument(
        "--output-location",
        default=None,
        help="Optional S3 output path for Athena results (for example s3://my-bucket/athena-results/).",
    )
    parser.add_argument("--output", default="docs/query_scan_comparison.md", help="Report path.")
    parser.add_argument("--region", default=None, help="Optional AWS region override.")
    parser.add_argument(
        "--broad-query",
        default="SELECT COUNT(*) FROM telemetry",
        help="Broad Athena query without partition filters.",
    )
    parser.add_argument(
        "--partitioned-query",
        default="SELECT COUNT(*) FROM telemetry WHERE year = 2024 AND month = 1",
        help="Partition-aware Athena query that filters by year and month.",
    )
    args = parser.parse_args()

    client_kwargs = {"region_name": args.region} if args.region else {}
    client = boto3.client("athena", **client_kwargs)

    broad_result = run_query(client, args.broad_query, args.database, args.workgroup, args.output_location)
    partitioned_result = run_query(client, args.partitioned_query, args.database, args.workgroup, args.output_location)

    report_path = build_report(args.output, broad_result, partitioned_result)
    print(report_path)


if __name__ == "__main__":
    main()
