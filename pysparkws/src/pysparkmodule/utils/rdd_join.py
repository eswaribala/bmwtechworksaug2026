from pyspark.sql import SparkSession


spark = (SparkSession.builder
         .appName("BMW Sensor Telemetry")
         #define cluster configuration
         .master("local[*]")
         .config("spark.executor.memory", "2g")
         .getOrCreate())

#rdd
sc=spark.sparkContext

#read sales data from a CSV file

sales_data = sc.textFile("src/pysparkmodule/data/bmw_sales_raw.csv",
                        minPartitions=4)

header=sales_data.first()

filtered_sales_data = sales_data.filter(lambda line: line != header)

#key value pair for sales data

sales_kv = (filtered_sales_data.map(lambda line: line.split(",")) 
           .map(lambda fields: (fields[2], (fields[1],fields[4]))))  # Assuming the first column is the key

master_data = sc.textFile("src/pysparkmodule/data/master_data.csv",
                        minPartitions=4)

header_master=master_data.first()

filtered_master_data = master_data.filter(lambda line: line != header_master)

master_kv = (filtered_master_data.map(lambda line: line.split(","))
           .map(lambda fields: (fields[0], (fields[1],fields[2]))))  # Assuming the first column is the key

#join the sales data with master data using the key

joined_data = sales_kv.join(master_kv)

#print("Joined Data:")
#for line in joined_data.collect():
   # print(line)

#flatten the joined data to get a single RDD with all the information

flattened_data = joined_data.map(lambda x: (x[0], x[1][0][0], x[1][0][1], x[1][1][0], x[1][1][1]))

#print("Flattened Data:")
for line in flattened_data.collect():
    print(line)
