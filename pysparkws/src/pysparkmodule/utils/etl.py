#create pyspark session


from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

spark = SparkSession.builder \
    .appName("ETL Application") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .master("local[*]") \
    .getOrCreate()

#read customer data from csv file
customer_df = spark.read.csv("src/data/bmw_customer_1000.csv", header=True, inferSchema=True)

#data cleaning

#drop the rows with null values in the customer data
customer_df = customer_df.dropna()

#drop the duplicate rows in the customer data
customer_df = customer_df.dropDuplicates()

#transform the customer data price to integer
customer_df = customer_df.withColumn("purchase_price_inr", col("purchase_price_inr").cast("integer"))

#based on the purchase price, create a new column called "purchase_category" with the following conditions:
# if purchase_price_inr < 1000000, then purchase_category = "budget"
# if purchase_price_inr >= 1000000 and purchase_price_inr < 5000000, then purchase_category = "premium"
# if purchase_price_inr >= 5000000, then purchase_category = "luxury"
customer_df = customer_df.withColumn("purchase_category", 
                                     when(col("purchase_price_inr") < 1000000, "budget")
                                     .when((col("purchase_price_inr") >= 1000000) 
                                    & (col("purchase_price_inr") < 5000000), "premium")
                                     .otherwise("luxury"))

#filter the customer data based purchase_date between 2023 to 2025
customer_df = customer_df.filter((col("purchase_date") >= "2023-01-01") 
                                 & (col("purchase_date") <= "2025-12-31"))

#save as parquet file in the reports folder
customer_df.write.mode("overwrite").parquet("src/reports/customer_data.parquet")