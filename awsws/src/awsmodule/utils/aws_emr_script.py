from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count
spark = SparkSession.builder \
.appName("BMWTelemetryEMR") \
.getOrCreate()
input_path = "s3://bmw-emr-lab-2026/raw/telemetry/"
output_path = "s3://bmw-emr-lab-2026/processed/telemetry/"
df = spark.read \
.option("header", True) \
.option("inferSchema", True) \
.csv(input_path)
print("BMW TELEMETRY")
df.show()
print("LOW BATTERY VEHICLES")
low_battery = df.filter(
df.battery_level < 20
)
low_battery.show()
print("HIGH TEMPERATURE VEHICLES")
high_temperature = df.filter(
df.temperature > 90
)

high_temperature.show()
print("MODEL ANALYSIS")
result = df.groupBy("model").agg(
count("vehicle_id").alias("vehicle_count"),
avg("battery_level").alias(
"average_battery"
),
avg("temperature").alias(
"average_temperature"
)
)
result.show()
result.write \
.mode("overwrite") \
.parquet(output_path)
spark.stop()