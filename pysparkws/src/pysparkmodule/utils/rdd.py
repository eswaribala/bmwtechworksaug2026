
from pyspark.sql import SparkSession

#create the driver
spark = (SparkSession.builder
         .appName("MyApp")
         .config("spark.sql.shuffle.partitions", "4")
         .config("spark.executor.memory", "2g")
         #cluster mode
         .master("local[*]")
         .getOrCreate()
        )

#create the RDD
context = spark.sparkContext

#read the text file
#data  partitions
rdd = context.textFile("src/pysparkmodule/data/bmw_customers_1000.csv", 
                       minPartitions=4)

split_rdd = rdd.map(lambda x: x.split("\n"))

#count the number of records in the RDD
count = split_rdd.count()
print(f"Number of records in the RDD: {count}")

#count the number of partitions in the RDD
num_partitions = split_rdd.getNumPartitions()

print(f"Number of partitions in the RDD: {num_partitions}")


