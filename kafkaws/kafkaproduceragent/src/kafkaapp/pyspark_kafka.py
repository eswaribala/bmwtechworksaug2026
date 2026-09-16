import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from py4j.protocol import Py4JError, Py4JNetworkError
from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import (
    col,
    current_timestamp,
    expr,
    to_date,
)


# =========================================================
# Project paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"

AVRO_SCHEMA_PATH = (
    PROJECT_ROOT
        / "customer_schema.avsc"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "output"
    / "processed"
    / "bmw_customers"
)

CHECKPOINT_DIRECTORY = (
    PROJECT_ROOT
    / "checkpoints"
    / "bmw_customers"
)


# =========================================================
# Load environment variables
# =========================================================

load_dotenv(ENV_PATH)

KRAFT_BOOTSTRAP_SERVERS = os.getenv(
    "KRAFT_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

KAFKA_AVRO_TOPIC = os.getenv(
    "KAFKA_AVRO_TOPIC",
    "salesqueue-avro",
)


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


# =========================================================
# Validation
# =========================================================

if not ENV_PATH.exists():
    logger.warning(
        ".env file was not found: %s",
        ENV_PATH,
    )

if not AVRO_SCHEMA_PATH.exists():
    raise FileNotFoundError(
        f"Avro schema file was not found: "
        f"{AVRO_SCHEMA_PATH}"
    )

if not KRAFT_BOOTSTRAP_SERVERS:
    raise ValueError(
        "KRAFT_BOOTSTRAP_SERVERS is missing"
    )

if not KAFKA_AVRO_TOPIC:
    raise ValueError(
        "KAFKA_AVRO_TOPIC is missing"
    )


# Read the Avro schema as JSON text.
avro_schema_json = AVRO_SCHEMA_PATH.read_text(
    encoding="utf-8"
)

# Spark creates these directories when the stream starts,
# but creating them here makes path validation easier.
OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

CHECKPOINT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# Create Spark session
# =========================================================

spark = (
    SparkSession.builder
    .appName("BMWCustomerKafkaToParquet")
    .master("local[*]")
    .config(
        "spark.sql.shuffle.partitions",
        "4",
    )
    .config(
        "spark.sql.adaptive.enabled",
        "false",
    )
    .config(
        "spark.jars.packages",
        ",".join(
            [
                (
                    "org.apache.spark:"
                    "spark-sql-kafka-0-10_2.13:"
                    "4.2.0"
                ),
                (
                    "org.apache.spark:"
                    "spark-avro_2.13:"
                    "4.2.0"
                ),
            ]
        ),
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# =========================================================
# Read binary messages from Kafka
# =========================================================

kafka_stream = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        KRAFT_BOOTSTRAP_SERVERS,
    )
    .option(
        "subscribe",
        KAFKA_AVRO_TOPIC,
    )
    .option(
        "startingOffsets",
        "earliest",
    )
    .option(
        "failOnDataLoss",
        "false",
    )
    .load()
)


# =========================================================
# Extract the Confluent Avro payload
# =========================================================
#
# Confluent Avro wire format:
#
# Byte 0      : magic byte
# Bytes 1–4   : Schema Registry schema ID
# Bytes 5...  : actual Avro payload
#
# Spark substring positions are one-based.
# Starting at position 6 removes the first five bytes.
# =========================================================

avro_payload_stream = kafka_stream.select(
    col("key")
    .cast("string")
    .alias("message_key"),

    expr(
        "substring(value, 6, length(value) - 5)"
    ).alias("avro_payload"),

    col("topic")
    .alias("kafka_topic"),

    col("partition")
    .alias("kafka_partition"),

    col("offset")
    .alias("kafka_offset"),

    col("timestamp")
    .alias("kafka_timestamp"),
)


# =========================================================
# Deserialize the Avro record
# =========================================================

decoded_stream = avro_payload_stream.select(
    col("message_key"),

    from_avro(
        col("avro_payload"),
        avro_schema_json,
    ).alias("customer"),

    col("kafka_topic"),
    col("kafka_partition"),
    col("kafka_offset"),
    col("kafka_timestamp"),
)


# =========================================================
# Select and transform customer columns
# =========================================================

processed_stream = (
    decoded_stream

    # Ignore records that could not be decoded.
    .filter(
        col("customer").isNotNull()
    )

    # Ensure the required customer ID exists.
    .filter(
        col("customer.customer_id").isNotNull()
    )

    .select(
        col("customer.customer_id")
        .alias("customer_id"),

        col("customer.customer_name")
        .alias("customer_name"),

        col("customer.address")
        .alias("address"),

        col("customer.email")
        .alias("email"),

        col("customer.dob")
        .alias("dob"),

        col("message_key"),
        col("kafka_topic"),
        col("kafka_partition"),
        col("kafka_offset"),
        col("kafka_timestamp"),

        current_timestamp()
        .alias("processed_at"),
    )

    # Use Kafka message date for Parquet partitioning.
    # This prevents __HIVE_DEFAULT_PARTITION__ when dob is null.
    .withColumn(
        "event_date",
        to_date(col("kafka_timestamp")),
    )
)


# =========================================================
# Print incoming records on the console
# =========================================================

console_query = (
    processed_stream.writeStream
    .queryName("bmw_customer_console")
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .option("numRows", "50")
    .trigger(
        processingTime="10 seconds"
    )
    .start()
)


# =========================================================
# Write incoming records to Parquet
# =========================================================

parquet_query = (
    processed_stream.writeStream
    .queryName("bmw_customer_parquet")
    .format("parquet")
    .outputMode("append")
    .option(
        "path",
        str(OUTPUT_DIRECTORY),
    )
    .option(
        "checkpointLocation",
        str(CHECKPOINT_DIRECTORY),
    )
    .partitionBy("event_date")
    .trigger(
        processingTime="10 seconds"
    )
    .start()
)


# =========================================================
# Application information
# =========================================================

print()
print("=" * 70)
print("BMW CUSTOMER KAFKA-TO-PARQUET STREAM STARTED")
print("=" * 70)
print(
    f"Kafka server : "
    f"{KRAFT_BOOTSTRAP_SERVERS}"
)
print(
    f"Kafka topic  : "
    f"{KAFKA_AVRO_TOPIC}"
)
print(
    f"Avro schema  : "
    f"{AVRO_SCHEMA_PATH}"
)
print(
    f"Output       : "
    f"{OUTPUT_DIRECTORY}"
)
print(
    f"Checkpoint   : "
    f"{CHECKPOINT_DIRECTORY}"
)
print("Trigger      : 10 seconds")
print("Press Ctrl+C once to stop")
print("=" * 70)
print()


# =========================================================
# Wait and perform graceful shutdown
# =========================================================

try:
    spark.streams.awaitAnyTermination()

except KeyboardInterrupt:
    logger.info(
        "Shutdown requested by the user"
    )

finally:
    logger.info(
        "Stopping Spark streaming queries"
    )

    for streaming_query in [
        console_query,
        parquet_query,
    ]:
        try:
            if streaming_query.isActive:
                streaming_query.stop()

        except (
            Py4JError,
            Py4JNetworkError,
            ConnectionError,
        ) as exc:
            logger.warning(
                "Spark JVM already stopped; "
                "query cleanup skipped: %s",
                exc,
            )

        except Exception as exc:
            logger.warning(
                "Unable to stop query cleanly: %s",
                exc,
            )

    try:
        spark.stop()

    except (
        Py4JError,
        Py4JNetworkError,
        ConnectionError,
    ) as exc:
        logger.warning(
            "Spark JVM already stopped; "
            "Spark cleanup skipped: %s",
            exc,
        )

    except Exception as exc:
        logger.warning(
            "Unable to stop Spark cleanly: %s",
            exc,
        )

    logger.info(
        "BMW customer streaming application stopped"
    )