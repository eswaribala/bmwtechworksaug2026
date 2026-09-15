from pathlib import Path
from dotenv import load_dotenv
import logging
import os
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
KRAFT_BOOTSTRAP_SERVERS = os.getenv("KRAFT_BOOTSTRAP_SERVERS")
KAFKA_AVRO_TOPIC = os.getenv("KAFKA_AVRO_TOPIC")

#define spark session
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType

spark = (SparkSession.builder 
    .appName("KafkaSparkApp") 
    .master("local[*]") 
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate())

spark.sparkContext.setLogLevel("INFO")

customer_data_struct= StructType([
    StructField("customer_id", IntegerType(), True),
    StructField("customer_name", StringType(), True),
    StructField("address", StringType(), True),
    StructField("email", StringType(), True),
    StructField("dob", DateType(), True)
])