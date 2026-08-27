#create flatmap using vehicle and telemetry data from bmw sensor telemetry data



from pyspark.sql import SparkSession


spark = (SparkSession.builder
         .appName("BMW Sensor Telemetry")
         #define cluster configuration
         .master("local[*]")
         .config("spark.executor.memory", "2g")
         .getOrCreate())

#rdd
sc=spark.sparkContext

#read the telemetry data from a CSV file
telemetry_data = sc.textFile("src/data/bmw_sensor_telemetry_data_100.txt",
                             minPartitions=4)

#flatmap the telemetry data to extract relevant information

telemetry_flatmap = telemetry_data.flatMap(lambda line: line.split("#")[1]\
                    .split(",") if len(line.split("#")) > 1 else [])

