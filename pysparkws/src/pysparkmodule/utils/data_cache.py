from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when
#driver memory and executor memory can be set in the spark session builder
spark = (SparkSession.builder 
    .appName("ETL Application") 
    .config("spark.executor.memory", "2g") 
    .config("spark.driver.memory", "2g") 
    .config("spark.sql.shuffle.partitions", "4") 
    #cluster mode can be set to local[*] to use all the available cores in the local machine
    .master("local[*]") 
    .getOrCreate())

df=spark.read.csv("src/pysparkmodule/data/bmw_customers_cleaned.csv", header=True, inferSchema=True)

#cache the data
df.cache()

#count the number of rows in the dataframe
row_count = df.count()

print(f"Number of rows in the dataframe: {row_count}")

#filter the data only for Mumbai

df_mumbai = df.filter(col("city") == "Mumbai")

#print

print(f"Number of rows in the Mumbai dataframe: {df_mumbai.count()}")
df_mumbai.show()