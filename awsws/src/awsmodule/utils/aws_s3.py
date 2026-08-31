#upload bmw connected cars csv to s3 bucket

import boto3

source_file_path = 'src/awsmodule/data/bmw_connected_cars.csv'
bucket_name = 'bmw-s3-bucket-2026'
s3_file_path = 'connecteddata/bmw_connected_cars.csv'
s3_client = boto3.client('s3',region_name='us-east-1')

try:
    s3_client.upload_file(source_file_path, bucket_name, s3_file_path)
    print(f"File {source_file_path} uploaded to S3 bucket {bucket_name} at {s3_file_path}")
except Exception as e:
    print(f"Error uploading file: {e}")
