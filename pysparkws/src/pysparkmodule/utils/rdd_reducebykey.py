#reduce by key using models and quantity


from pyspark.sql import SparkSession

"""
spark = (SparkSession.builder
         .appName("BMW Sensor Telemetry")
         #define cluster configuration
         .master("local[*]")
         .config("spark.executor.memory", "2g")
         .getOrCreate())
"""
spark = (SparkSession.builder
         .appName("BMW Sensor Telemetry")
         #define cluster configuration
         .master("spark://spark-master:7077")
         .config("spark.executor.memory", "2g")
         .getOrCreate())

#rdd
sc=spark.sparkContext

#read the telemetry data from a CSV file
sales_data = sc.textFile("hdfs://namenode:9000/bmw/input/bmw_sales_raw.csv",minPartitions=4)

header=sales_data.first()  # extract header

#filter out the header from the RDD
sales_data_filtered = sales_data.filter(lambda line: line != header)

#reduce by key to aggregate the quantity sold for each model
sales_reducebykey = sales_data_filtered.map(
    lambda line: line.split(",")
).map(
    lambda fields: (fields[2], int(fields[7]))  # assuming model is in the second column and quantity in the third column
).reduceByKey(
    lambda a, b: a + b
)

print("Total quantity sold for each model:")
for model, total_quantity in sales_reducebykey.collect():
    print(f"Model: {model}, Total Quantity Sold: {total_quantity}")