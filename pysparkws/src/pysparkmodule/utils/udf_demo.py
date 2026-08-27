#create pyspark session


from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
#driver memory and executor memory can be set in the spark session builder
spark = (SparkSession.builder 
    .appName("ETL Application") 
    .config("spark.executor.memory", "2g") 
    .config("spark.driver.memory", "2g") 
    .config("spark.sql.shuffle.partitions", "4") 
    #cluster mode can be set to local[*] to use all the available cores in the local machine
    .master("local[*]") 
    .getOrCreate())

#read customer data from csv file
#executors
customer_df = spark.read.csv("src/pysparkmodule/data/bmw_customers_1000.csv", header=True, inferSchema=True)

#data cleaning

#drop the rows with null values in the customer data
customer_df = customer_df.dropna()

#drop the duplicate rows in the customer data
customer_df = customer_df.dropDuplicates()

def classify_purchase_category(price):
    if price < 1000000:
        return "budget"
    elif price >= 1000000 and price < 5000000:
        return "premium"
    else:
        return "luxury"

#creat a udf to classify the purchase category based on the purchase price

classify_purchase_category_udf = udf(classify_purchase_category, StringType())

#based on the purchase price, create a new column called "purchase_category" with the following conditions:
# if purchase_price_inr < 1000000, then purchase_category = "budget"
customer_df = customer_df.withColumn("purchase_category", classify_purchase_category_udf(col("purchase_price_inr")))

#print the schema of the customer data
customer_df.show()