"""Start a Glue ETL job via the AWS SDK."""

from __future__ import annotations

import argparse

import boto3


def start_glue_job(job_name: str) -> dict:
    """Start a Glue ETL job and return the response."""

    glue = boto3.client("glue")
    response = glue.start_job_run(JobName=job_name)
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a Glue ETL job for the BMW data lake.")
    parser.add_argument("--job-name", required=True, help="Name of the Glue ETL job to start.")
    args = parser.parse_args()

    response = start_glue_job(args.job_name)
    print(response)


if __name__ == "__main__":
    main()
