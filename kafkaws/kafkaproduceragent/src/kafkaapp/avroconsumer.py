#create avro consumer for customer events
import logging
import os
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
from pathlib import Path

from dotenv import load_dotenv
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
SCHEMA_PATH = PROJECT_ROOT / "customer_schema.avsc"

load_dotenv(ENV_PATH)



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

KRAFT_BOOTSTRAP_SERVERS = os.getenv("KRAFT_BOOTSTRAP_SERVERS")


KAFKA_AVRO_TOPIC = os.getenv("KAFKA_AVRO_TOPIC")

SCHEMA_REGISTRY_CLIENT=os.getenv("KAFKA_SCHEMA_REGISTRY_URL")

if not KRAFT_BOOTSTRAP_SERVERS:
    logger.error("KRAFT_BOOTSTRAP_SERVERS is not set")

if not KAFKA_AVRO_TOPIC:
    logger.error("KAFKA_AVRO_TOPIC is not set")

#deserializer

Schema_Registry_Client = SchemaRegistryClient(
    {"url": SCHEMA_REGISTRY_CLIENT}
)
Avro_Deserializer = AvroDeserializer(
    schema_registry_client=Schema_Registry_Client,
    
)
String_Deserializer = StringDeserializer('utf_8')

consumer = DeserializingConsumer(
    {
        "bootstrap.servers": KRAFT_BOOTSTRAP_SERVERS,
        "key.deserializer": String_Deserializer,
        "value.deserializer": Avro_Deserializer,
        "group.id": "customer_event_group",
        "auto.offset.reset": "earliest"
    }
)
consumer.subscribe([KAFKA_AVRO_TOPIC])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Consumer error: {msg.error()}")
            continue
        logger.info(f"Consumed record with key {msg.key()}: {msg.value()}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
