from __future__ import annotations

import os
import time

import boto3


DATABASE = os.getenv("ATHENA_DATABASE", "ev_battery_health")
OUTPUT_LOCATION = os.getenv(
    "ATHENA_OUTPUT_LOCATION",
    "s3://ev-battery-health-data/athena-results/",
)
REGION = os.getenv("AWS_REGION", "eu-north-1")


def run_query(query: str) -> list[dict]:
    """Run an Athena query and return the result rows as dictionaries."""
    client = boto3.client("athena", region_name=REGION)
    execution = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": OUTPUT_LOCATION},
    )
    query_execution_id = execution["QueryExecutionId"]

    while True:
        status = client.get_query_execution(QueryExecutionId=query_execution_id)
        state = status["QueryExecution"]["Status"]["State"]
        if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        reason = status["QueryExecution"]["Status"].get(
            "StateChangeReason", "Unknown Athena error"
        )
        raise RuntimeError(f"Athena query {state}: {reason}")

    response = client.get_query_results(QueryExecutionId=query_execution_id)
    rows = response["ResultSet"]["Rows"]
    if not rows:
        return []

    headers = [field.get("VarCharValue", "") for field in rows[0]["Data"]]
    return [
        {
            header: (
                row["Data"][index].get("VarCharValue", "")
                if index < len(row["Data"])
                else ""
            )
            for index, header in enumerate(headers)
        }
        for row in rows[1:]
    ]


if __name__ == "__main__":
    results = run_query(
        """
        SELECT battery_health_category, COUNT(*) AS vehicle_count
        FROM vehicle_health
        GROUP BY battery_health_category
        ORDER BY battery_health_category
        """
    )
    for row in results:
        print(row)
