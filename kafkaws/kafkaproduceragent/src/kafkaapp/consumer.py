from confluent_kafka import Consumer
from pathlib import Path

from dotenv import load_dotenv
import os
import logging
from dotenv import load_dotenv

PROJECT_ROOT=Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

TOPIC = os.getenv("KAFKA_TOPIC")


consumer = Consumer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    "group.id": "bmw-consumer-group",
    "auto.offset.reset": "earliest",
})

consumer.subscribe([TOPIC])

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