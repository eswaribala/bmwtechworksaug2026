import os
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv
import logging
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer


CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
SCHEMA_PATH = PROJECT_ROOT / "customer_schema.avsc"

load_dotenv(ENV_PATH)



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

KRAFT_BOOTSTRAP_SERVERS = os.getenv("KRAFT_BOOTSTRAP_SERVERS")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", SCHEMA_PATH)

KAFKA_AVRO_TOPIC = os.getenv("KAFKA_AVRO_TOPIC")

SCHEMA_REGISTRY_CLIENT=os.getenv("KAFKA_SCHEMA_REGISTRY_URL")

if not KRAFT_BOOTSTRAP_SERVERS:
    logger.error("KRAFT_BOOTSTRAP_SERVERS is not set")
if not SCHEMA_PATH:
    logger.error("SCHEMA_PATH is not set")
if not KAFKA_AVRO_TOPIC:
    logger.error("KAFKA_AVRO_TOPIC is not set")

if not SCHEMA_PATH or not Path(SCHEMA_PATH).exists():
    logger.error("SCHEMA_PATH does not exist")

#read schema
SALES_AVRO_SCHEMA=Path(SCHEMA_PATH).read_text(encoding="utf-8") if SCHEMA_PATH and Path(SCHEMA_PATH).exists() else None
#Schema Registry Client
Schema_Registry_Client = SchemaRegistryClient(
    {"url": SCHEMA_REGISTRY_CLIENT}
)

#avro serializer
Avro_Serializer = AvroSerializer(
    schema_registry_client=Schema_Registry_Client,
    schema_str=SALES_AVRO_SCHEMA
)

String_Serializer = StringSerializer('utf_8')

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed for record {msg.key()}: {err}")
    else:
        logger.info(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}]")

producer = SerializingProducer(
    {
        "bootstrap.servers": KRAFT_BOOTSTRAP_SERVERS,
        "key.serializer": String_Serializer,
        "value.serializer": Avro_Serializer,
        "acks": "all"
    }
)
def date_to_avro_days(date_string: str) -> int:
    parsed_date = datetime.strptime(date_string, "%Y-%m-%d").date()
    return (parsed_date - date(1970, 1, 1)).days

customer_event={
    "customer_id": 12347,
    "customer_name": "Parameswari",
    "address": "123 Main St",
    "email": "parameswari@example.com",
    "dob": date_to_avro_days("1970-01-01")
}
producer.produce(
    topic=KAFKA_AVRO_TOPIC,
    key=str(customer_event["customer_id"]),
    value=customer_event,
    on_delivery=delivery_report
)
producer.flush()


