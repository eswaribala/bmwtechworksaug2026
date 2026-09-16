#!/usr/bin/env python3
"""
BMW Data Quality & Governance Platform — CSV Upload Script
Participant 12 | Pod D

Uploads the BMW sample CSV files to the S3 raw/ prefix.
Run this AFTER `terraform apply` to bootstrap the data lake with sample data.

Usage:
    python scripts/upload_csv.py --bucket <bucket-name>
    python scripts/upload_csv.py --bucket <bucket-name> --profile my-aws-profile
    python scripts/upload_csv.py --bucket <bucket-name> --dry-run

Requirements:
    pip install boto3 tqdm
"""

import argparse
import sys
import os
from pathlib import Path

# ── Dependency check ───────────────────────────────────────────────────────────
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("[ERROR] boto3 not installed. Run: pip install boto3")
    sys.exit(1)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ── File mapping: local path → S3 key ─────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent

FILE_MAP = {
    "data/sample/bmw_telemetry.csv":      "raw/telemetry/bmw_telemetry.csv",
    "data/sample/bmw_telemetry_demo.csv": "raw/telemetry/bmw_telemetry_demo.csv",
    "data/sample/bmw_vehicle_master.csv": "raw/vehicle_master/bmw_vehicle_master.csv",
}


def upload_file(s3_client, local_path: Path, bucket: str, s3_key: str, dry_run: bool) -> bool:
    """Upload a single file to S3. Returns True on success."""
    if not local_path.exists():
        print(f"  [SKIP]  {local_path} — file not found locally")
        return False

    file_size_mb = local_path.stat().st_size / (1024 * 1024)
    s3_uri = f"s3://{bucket}/{s3_key}"

    if dry_run:
        print(f"  [DRY-RUN] Would upload {local_path.name} ({file_size_mb:.1f} MB) → {s3_uri}")
        return True

    print(f"  Uploading {local_path.name} ({file_size_mb:.1f} MB) → {s3_uri}")

    try:
        if HAS_TQDM and file_size_mb > 1:
            # Show progress bar for large files
            with tqdm(total=local_path.stat().st_size, unit="B", unit_scale=True,
                      desc=local_path.name, ncols=80) as pbar:
                s3_client.upload_file(
                    str(local_path),
                    bucket,
                    s3_key,
                    Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
                )
        else:
            s3_client.upload_file(str(local_path), bucket, s3_key)

        print(f"  [OK]    {s3_uri}")
        return True

    except ClientError as e:
        print(f"  [ERROR] Upload failed: {e}")
        return False


def verify_bucket(s3_client, bucket: str) -> bool:
    """Check the bucket exists and we have access."""
    try:
        s3_client.head_bucket(Bucket=bucket)
        return True
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "404":
            print(f"[ERROR] Bucket '{bucket}' does not exist. Run terraform apply first.")
        elif code in ("403", "AccessDenied"):
            print(f"[ERROR] Access denied to bucket '{bucket}'. Check IAM permissions.")
        else:
            print(f"[ERROR] Could not access bucket: {e}")
        return False


def list_bucket_contents(s3_client, bucket: str, prefix: str = "raw/"):
    """Print the objects currently in S3 under the given prefix."""
    print(f"\nCurrent objects in s3://{bucket}/{prefix}:")
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        count = 0
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                size_kb = obj["Size"] / 1024
                print(f"  {obj['Key']}  ({size_kb:.1f} KB)  {obj['LastModified'].strftime('%Y-%m-%d %H:%M')}")
                count += 1
        if count == 0:
            print("  (empty)")
        print()
    except ClientError as e:
        print(f"  [WARN] Could not list bucket: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Upload BMW CSV sample data to S3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--bucket", "-b",
        required=True,
        help="S3 bucket name (output of terraform apply: s3_bucket_name)",
    )
    parser.add_argument(
        "--profile", "-p",
        default=None,
        help="AWS CLI profile to use (default: uses default profile / env vars)",
    )
    parser.add_argument(
        "--region", "-r",
        default="eu-central-1",
        help="AWS region (default: eu-central-1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be uploaded without actually uploading",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing files in the bucket after upload",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("BMW Data Quality — S3 CSV Upload Script")
    print("Participant 12 | Pod D")
    print("=" * 60)
    print(f"  Bucket  : {args.bucket}")
    print(f"  Region  : {args.region}")
    print(f"  Profile : {args.profile or 'default'}")
    print(f"  Dry run : {args.dry_run}")
    print()

    # ── Create boto3 session ──────────────────────────────────────────────────
    try:
        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        s3 = session.client("s3")
    except NoCredentialsError:
        print("[ERROR] AWS credentials not found.")
        print("  Run `aws configure` or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars.")
        sys.exit(1)

    # ── Verify bucket exists ──────────────────────────────────────────────────
    if not args.dry_run:
        if not verify_bucket(s3, args.bucket):
            sys.exit(1)

    # ── Upload files ──────────────────────────────────────────────────────────
    success = 0
    failed = 0

    for rel_path, s3_key in FILE_MAP.items():
        local_path = PROJECT_ROOT / rel_path
        ok = upload_file(s3, local_path, args.bucket, s3_key, dry_run=args.dry_run)
        if ok:
            success += 1
        else:
            failed += 1

    print()
    print(f"Upload complete: {success} succeeded, {failed} skipped/failed")

    # ── List bucket contents ──────────────────────────────────────────────────
    if args.list and not args.dry_run:
        list_bucket_contents(s3, args.bucket, prefix="raw/")

    print()
    print("Next steps:")
    print(f"  1. Run the pipeline:")
    print(f"     python src/main.py --dataset telemetry --s3-key raw/telemetry/bmw_telemetry_demo.csv")
    print(f"  2. Open the CloudWatch dashboard to monitor quality scores.")
    print(f"  3. Query data with Athena using the Glue catalog.")
    print()


if __name__ == "__main__":
    main()
