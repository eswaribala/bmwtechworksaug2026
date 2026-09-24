"""Amazon S3 helper functions used by the ingestion layer.

The module creates a boto3 S3 client using ``AWS_REGION`` and exposes a
small upload helper so application code does not need to repeat bucket
configuration or S3 URI construction.
"""

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))

def upload_file(local_path: str, key: str):
    """Upload a local file to the configured S3 bucket and return its S3 URI."""
    bucket = os.environ["S3_BUCKET_NAME"]
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"
