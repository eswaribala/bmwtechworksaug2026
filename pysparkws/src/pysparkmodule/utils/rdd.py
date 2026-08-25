
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
rdd = context.textFile("src/pysparkmodule/data/bmw_customers_1000.csv", 
                       minPartitions=4)
#remove the header from the RDD
header = rdd.first()

split_rdd = rdd.filter(lambda x: x != header).map(lambda x: x.split("\n"))

#count the number of records in the RDD
count = split_rdd.count()
print(f"Number of records in the RDD: {count}")

#count the number of partitions in the RDD
num_partitions = split_rdd.getNumPartitions()

print(f"Number of partitions in the RDD: {num_partitions}")

def simulate_failure(iterator):
    context = TaskContext.get()
    partition_id = context.partitionId()
    attempt_number = context.attemptNumber()
    print(f"Processing partition {partition_id}, attempt {attempt_number}")
    if partition_id == 2 and attempt_number == 0:
        raise Exception("Simulated failure in partition 2")
    for record in iterator:
        yield record

split_rdd_with_failure = split_rdd.mapPartitions(simulate_failure)

#prove that failure is handled by Spark and the job is retried
#fault tolerance
try:
    result = split_rdd_with_failure.collect()
    #print(f"Result: {result}")
    #count the number of records in the RDD after failure handling
    count_after_failure = len(result)
    print(f"Number of records in the RDD after failure handling: {count_after_failure}")
    #count the number of partitions in the RDD after failure handling
    num_partitions_after_failure = split_rdd_with_failure.getNumPartitions()
    print(f"Number of partitions in the RDD after failure handling: {num_partitions_after_failure}")
except Exception as e:
    print(f"Job failed with exception: {e}")



