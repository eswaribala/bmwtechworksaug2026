"""Upload local BMW raw data to an S3 raw prefix."""

from __future__ import annotations

import argparse
from pathlib import Path

import boto3


def upload_directory(local_dir: str | Path, bucket_name: str, prefix: str = "raw") -> list[str]:
    """Upload all CSV files in a directory to an S3 prefix."""

    s3 = boto3.client("s3")
    local_path = Path(local_dir)
    uploaded: list[str] = []

    for file_path in sorted(local_path.glob("*.csv")):
        key = f"{prefix}/{file_path.name}"
        s3.upload_file(str(file_path), bucket_name, key)
        uploaded.append(f"s3://{bucket_name}/{key}")

    return uploaded


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload BMW raw CSV files to S3.")
    parser.add_argument("--local-dir", default=str(Path("data/generated")), help="Local directory with raw BMW CSV files.")
    parser.add_argument("--bucket", required=True, help="S3 bucket name for the raw data lake zone.")
    parser.add_argument("--prefix", default="raw", help="S3 prefix to store raw data under.")
    args = parser.parse_args()

    uploaded = upload_directory(args.local_dir, args.bucket, prefix=args.prefix)
    for item in uploaded:
        print(item)


if __name__ == "__main__":
    main()
