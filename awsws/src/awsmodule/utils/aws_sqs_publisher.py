import boto3
import json

sqs = boto3.client("sqs", region_name="us-east-1")

response = sqs.get_queue_url(
    QueueName="telemetryqueue"
)

queue_url = response["QueueUrl"]

telemetry = {
    "vehicle_id": "BMW4005",
    "model": "BMW ix7",
    "battery_level": 12,
    "temperature": 88,
    "speed": 70
}

response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps(telemetry)
)

print(response["MessageId"])