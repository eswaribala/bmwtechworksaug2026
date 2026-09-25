import json
import time

import boto3

session = boto3.Session(profile_name="default")
ath = session.client("athena", region_name="us-east-1")
query = 'SELECT count(*) AS row_count FROM "bmw-serverless-data-lake_dev"."curated"'

print("QUERY:", query)
resp = ath.start_query_execution(
    QueryString=query,
    QueryExecutionContext={"Database": "bmw-serverless-data-lake_dev"},
    ResultConfiguration={
        "OutputLocation": "s3://bmw-serverless-data-lake-dev-bmw-data-lake-dev/athena-results/"
    },
    WorkGroup="bmw-serverless-data-lake-dev-analytics",
)
print(json.dumps(resp, default=str))
qid = resp["QueryExecutionId"]

for i in range(20):
    r = ath.get_query_execution(QueryExecutionId=qid)
    state = r["QueryExecution"]["Status"]["State"]
    print("STATE:", state)
    print(json.dumps(r, default=str))
    if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
        break
    time.sleep(5)
