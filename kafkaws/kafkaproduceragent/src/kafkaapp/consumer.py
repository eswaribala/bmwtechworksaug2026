from socket import socket

from confluent_kafka import Consumer
from pathlib import Path
from datetime import datetime, timezone
import signal

from dotenv import load_dotenv
import os
import logging
from dotenv import load_dotenv
import boto3

PROJECT_ROOT=Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

TOPIC = os.getenv("KAFKA_TOPIC")

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))

running=True

consumer = Consumer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    "broker.address.family": "v4",
    "group.id": "bmw-consumer-group",
    "client.id": socket.gethostname(),
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})


consumer.subscribe([TOPIC])

s3_client = boto3.client("s3", region_name=AWS_REGION)


def stop_consumer(signum, frame):
    global running
    logger.info("Stopping consumer requested...")
    running = False

def s3_bucket_key()->str:
    now = datetime.now(timezone.utc)
    return (
        f"{S3_PREFIX}"
        f"year={now.year}/"
        f"month={now.month}/"
        f"day={now.day}/"
        f"hour={now.hour}/"
        f"minute={now.minute}/"
        f"second={now.second}/"
        f"sales-{now.strftime('%Y%m%d%H%M%S')}.json"
    )



try:
    while True:
        message = consumer.poll(1.0)

        if message is None:
            continue

        if message.error():
            print("Error:", message.error())
            continue

        if message.value() is not None:
            print(message.value().decode("utf-8"))

except KeyboardInterrupt:
    pass

finally:
    consumer.close()