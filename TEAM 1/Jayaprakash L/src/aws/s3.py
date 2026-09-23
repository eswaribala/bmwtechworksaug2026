import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))

def upload_file(local_path: str, key: str):
    bucket = os.environ["S3_BUCKET_NAME"]
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"
