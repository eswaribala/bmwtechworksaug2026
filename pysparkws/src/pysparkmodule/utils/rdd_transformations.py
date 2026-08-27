from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("BMW Sensor RDD")
    .config("spark.executor.memory", "2g")
    .master("local[*]")
    .getOrCreate()
)

context = spark.sparkContext

# Read BMW sensor raw data
rdd = context.textFile(
    "src/pysparkmodule/data/bmw_sensor_raw_data.txt",
    minPartitions=4
)

# Remove header
header = rdd.first()

split_rdd = (
    rdd
    .filter(lambda x: x != header)
    .map(lambda x: x.split("#"))
)

print(f"Number of records in the RDD: {split_rdd.count()}")
print(f"Number of partitions in the RDD: {split_rdd.getNumPartitions()}")

# ---------------------------------------------------
# vehicle_id = column 0
# engine_rpm = column 3
# ---------------------------------------------------

rpm_rdd = split_rdd.map(
    lambda x: (x[0], int(x[3]))
)

print("Sample key-value pairs:")
for row in rpm_rdd.take(5):
    print(row)

# Group RPM values by vehicle
grouped_rdd = rpm_rdd.groupByKey()

# Calculate average RPM
average_rpm_by_car = grouped_rdd.mapValues(
    lambda rpms: sum(rpms) / len(rpms)
)

print("\nAverage Engine RPM by BMW:")

for adas, avg_rpm in average_rpm_by_car.collect():
    print(
        f"ADAS: {adas}, "
        f"Average Engine RPM: {avg_rpm:.2f}"
    )

spark.stop()