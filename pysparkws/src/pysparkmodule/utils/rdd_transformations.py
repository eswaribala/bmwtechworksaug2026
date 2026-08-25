
from pyspark import TaskContext
from pyspark.sql import SparkSession

#create the driver
spark = (SparkSession.builder
         .appName("MyApp")
         .config("spark.sql.shuffle.partitions", "4")
         .config("spark.executor.memory", "2g")
         #cluster mode
         .master("local[4,4]")
         .getOrCreate()
        )

#create the RDD
context = spark.sparkContext

#read the text file
#data  partitions
rdd = context.textFile("src/pysparkmodule/data/bmw_sensor_raw_data.txt", 
                       minPartitions=4)
#remove the header from the RDD
header = rdd.first()

split_rdd = rdd.filter(lambda x: x != header).map(lambda x: x.split("#"))

#count the number of records in the RDD
count = split_rdd.count()
print(f"Number of records in the RDD: {count}")

#count the number of partitions in the RDD
num_partitions = split_rdd.getNumPartitions()

print(f"Number of partitions in the RDD: {num_partitions}")

#group the cars by vehicle_id column 0
split_rdd_with_key = split_rdd.map(lambda x: (x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16],x[17],x[18],x[19],x[20],x[21],x[22]))     

grouped_rdd = split_rdd_with_key.groupByKey()

#find average engine rpm
average_rpm_by_car = grouped_rdd.mapValues(lambda records: sum(int(record[1]) for record in records) / len(records))

for car_id, avg_rpm in average_rpm_by_car.collect():
    print(f"Car ID: {car_id}, Average Engine RPM: {avg_rpm}")