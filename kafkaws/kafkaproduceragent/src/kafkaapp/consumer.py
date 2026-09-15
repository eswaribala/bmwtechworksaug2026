from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import json
import logging
import os
import platform
import signal

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from confluent_kafka import Consumer, KafkaError, KafkaException
from dotenv import load_dotenv


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

TOPIC = os.getenv(
    "KAFKA_TOPIC",
    "salesqueue",
)

CONSUMER_GROUP = os.getenv(
    "KAFKA_CONSUMER_GROUP",
    "sales-s3-consumer-v1",
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1",
)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

S3_PREFIX = os.getenv(
    "S3_PREFIX",
    "raw/salesadata",
).strip("/")

# Use 1 for testing so every message is uploaded immediately.
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))

if not S3_BUCKET_NAME:
    raise ValueError(
        "S3_BUCKET_NAME is missing from the .env file"
    )

if not TOPIC:
    raise ValueError(
        "KAFKA_TOPIC is missing from the .env file"
    )


# ---------------------------------------------------------
# Kafka and S3 clients
# ---------------------------------------------------------

running = True

consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "broker.address.family": "v4",
        "group.id": CONSUMER_GROUP,
        "client.id": platform.node() or "sales-s3-consumer",
        "auto.offset.reset": "earliest",

        # Commit Kafka offsets only after S3 upload.
        "enable.auto.commit": False,
    }
)

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
)


# ---------------------------------------------------------
# Shutdown handler
# ---------------------------------------------------------

def stop_consumer(signum, frame):
    global running

    logger.info("Shutdown requested...")
    running = False


# ---------------------------------------------------------
# Generate a unique S3 object key
# ---------------------------------------------------------

def create_s3_key() -> str:
    now = datetime.now(timezone.utc)

    return (
        f"{S3_PREFIX}/"
        f"year={now:%Y}/"
        f"month={now:%m}/"
        f"day={now:%d}/"
        f"hour={now:%H}/"
        f"sales-{now:%Y%m%dT%H%M%S%fZ}.jsonl"
    )


# ---------------------------------------------------------
# Upload one batch to S3
# ---------------------------------------------------------

def upload_batch(records: list[dict]) -> str:
    json_lines = "\n".join(
        json.dumps(
            record,
            separators=(",", ":"),
            default=str,
        )
        for record in records
    )

    body = BytesIO(
        (json_lines + "\n").encode("utf-8")
    )

    s3_key = create_s3_key()

    s3_client.upload_fileobj(
        body,
        S3_BUCKET_NAME,
        s3_key,
        ExtraArgs={
            "ContentType": "application/x-ndjson",
            "ServerSideEncryption": "AES256",
        },
    )

    return s3_key


# ---------------------------------------------------------
# Extract sales event from Kafka message
# ---------------------------------------------------------

def extract_sales_event(decoded_message: dict) -> dict:
    """
    Supports both formats:

    Direct event:
    {
        "product_id": 2004,
        "quantity": 5,
        ...
    }

    Wrapped event:
    {
        "status": "delivered",
        "event": {
            "product_id": 2004,
            ...
        }
    }
    """

    event = decoded_message.get("event", decoded_message)

    if not isinstance(event, dict):
        raise ValueError("The sales event must be a JSON object")

    return event


# ---------------------------------------------------------
# Kafka consumer
# ---------------------------------------------------------

def consume_to_s3():
    batch: list[dict] = []

    consumer.subscribe([TOPIC])

    logger.info(
        "Consumer started: topic=%s group=%s Kafka=%s",
        TOPIC,
        CONSUMER_GROUP,
        KAFKA_BOOTSTRAP_SERVERS,
    )

    logger.info(
        "S3 destination: s3://%s/%s/",
        S3_BUCKET_NAME,
        S3_PREFIX,
    )

    logger.info(
        "Batch size: %s",
        BATCH_SIZE,
    )

    try:
        while running:
            message = consumer.poll(timeout=1.0)

            if message is None:
                continue

            if message.error():
                if (
                    message.error().code()
                    == KafkaError._PARTITION_EOF
                ):
                    continue

                raise KafkaException(message.error())

            try:
                decoded_message = json.loads(
                    message.value().decode("utf-8")
                )

                sales_event = extract_sales_event(
                    decoded_message
                )

            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
                ValueError,
            ) as exc:
                logger.error(
                    "Invalid sales message: "
                    "partition=%s offset=%s error=%s",
                    message.partition(),
                    message.offset(),
                    exc,
                )
                continue

            record = {
                **sales_event,
                "_kafka": {
                    "topic": message.topic(),
                    "partition": message.partition(),
                    "offset": message.offset(),
                    "timestamp": message.timestamp()[1],
                },
            }

            batch.append(record)

            logger.info(
                "Received product=%s quantity=%s "
                "price=%s total=%s region=%s "
                "partition=%s offset=%s batch=%s/%s",
                sales_event.get("product_id"),
                sales_event.get("quantity"),
                sales_event.get("price"),
                sales_event.get("total"),
                sales_event.get("region"),
                message.partition(),
                message.offset(),
                len(batch),
                BATCH_SIZE,
            )

            if len(batch) >= BATCH_SIZE:
                s3_key = upload_batch(batch)

                # Commit offsets only after successful upload.
                consumer.commit(asynchronous=False)

                logger.info(
                    "Uploaded %s record(s) to s3://%s/%s",
                    len(batch),
                    S3_BUCKET_NAME,
                    s3_key,
                )

                batch.clear()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    except (BotoCoreError, ClientError) as exc:
        logger.exception(
            "S3 operation failed: %s",
            exc,
        )
        raise

    except KafkaException as exc:
        logger.exception(
            "Kafka consumer failed: %s",
            exc,
        )
        raise

    finally:
        # Upload records remaining below BATCH_SIZE.
        if batch:
            try:
                s3_key = upload_batch(batch)
                consumer.commit(asynchronous=False)

                logger.info(
                    "Uploaded final %s record(s) to s3://%s/%s",
                    len(batch),
                    S3_BUCKET_NAME,
                    s3_key,
                )

            except Exception:
                logger.exception(
                    "Final batch upload failed"
                )

        consumer.close()
        logger.info("Consumer stopped")


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    signal.signal(
        signal.SIGINT,
        stop_consumer,
    )

    signal.signal(
        signal.SIGTERM,
        stop_consumer,
    )

    consume_to_s3()