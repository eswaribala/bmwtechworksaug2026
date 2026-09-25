"""Run an Athena query using the AWS SDK."""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

import boto3


def summarize_execution(result: dict[str, Any]) -> dict[str, Any]:
    """Extract a compact summary of the Athena execution details."""
    execution = result["QueryExecution"]
    status = execution["Status"]
    statistics = execution.get("Statistics", {})
    return {
        "query_execution_id": execution["QueryExecutionId"],
        "state": status["State"],
        "state_change_reason": status.get("StateChangeReason"),
        "statement_type": execution.get("StatementType"),
        "data_scanned_in_bytes": statistics.get("DataScannedInBytes"),
        "engine_version": execution.get("EngineVersion", {}).get("EffectiveEngineVersion"),
        "result_location": execution.get("ResultConfiguration", {}).get("OutputLocation"),
        "submission_date_time": execution.get("SubmissionDateTime"),
        "completion_date_time": execution.get("CompletionDateTime"),
    }


def run_query(client, query: str, workgroup: str, database: str, output_location: str | None = None) -> dict[str, Any]:
    """Execute an Athena query and wait until completion."""

    request = {
        "QueryString": query,
        "QueryExecutionContext": {"Database": database},
        "WorkGroup": workgroup,
    }
    if output_location:
        request["ResultConfiguration"] = {"OutputLocation": output_location}

    response = client.start_query_execution(**request)
    execution_id = response["QueryExecutionId"]

    while True:
        result = client.get_query_execution(QueryExecutionId=execution_id)
        state = result["QueryExecution"]["Status"]["State"]
        if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            return result
        time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an Athena SQL query.")
    parser.add_argument("--query", required=True, help="SQL query to run.")
    parser.add_argument("--database", required=True, help="Glue catalog database name.")
    parser.add_argument("--workgroup", default="primary", help="Athena workgroup name.")
    parser.add_argument(
        "--output-location",
        default=None,
        help="Optional S3 output path for Athena results (for example s3://my-bucket/athena-results/).",
    )
    parser.add_argument("--region", default=None, help="Optional AWS region override.")
    args = parser.parse_args()

    client_kwargs = {"region_name": args.region} if args.region else {}
    client = boto3.client("athena", **client_kwargs)
    result = run_query(client, args.query, args.workgroup, args.database, args.output_location)
    print(json.dumps(summarize_execution(result), indent=2, default=str))


if __name__ == "__main__":
    main()
