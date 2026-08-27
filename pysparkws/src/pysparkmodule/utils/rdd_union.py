from pyspark.sql import SparkSession


spark = (SparkSession.builder
         .appName("BMW Sensor Telemetry")
         #define cluster configuration
         .master("local[*]")
         .config("spark.executor.memory", "2g")
         .getOrCreate())

#rdd
sc=spark.sparkContext

#read chennai plant telemetry data from a CSV file
chennai_plant_telemetry_data = sc.textFile("src/pysparkmodule/data/bmw_chennai_plant_raw_telemetry_100.csv",
                                           minPartitions=4)

#read pune plant telemetry data from a CSV file
pune_plant_telemetry_data = sc.textFile("src/pysparkmodule/data/bmw_pune_plant_raw_telemetry_100.csv",
                                        minPartitions=4)

#union the two RDDs
union_telemetry_data = chennai_plant_telemetry_data.union(pune_plant_telemetry_data)

#print the unioned telemetry data
for line in union_telemetry_data.collect():
    print(line)