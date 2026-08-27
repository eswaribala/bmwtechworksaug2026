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

sc= spark.sparkContext

#read the file
rdd_data=(sc.textFile("src/pysparkmodule/data/bmw_customers_cleaned.csv",
                      minPartitions=4))

header=rdd_data.first()

split_header=header.split(",")

#broadcast variable

state_broadcast_data={
    "Tamil Nadu": "TN",
    "Kerala": "KL",
    "Karnataka": "KA",
    "Telangana": "TS",
    "Maharashtra": "MH",
    "Haryana": "HR",
    "Rajasthan": "RJ",
    "Gujarat": "GJ",
    "Uttar Pradesh": "UP",
    "Bihar": "BR",
    "Delhi": "DL",
    "West Bengal": "WB",
    "Chandigarh": "CH",
    "Andhra Pradesh": "AP"
}
#map to column 7 with broadcast variable
data=rdd_data.filter(lambda x: x != header).map(lambda x: (x.split(",")[0], x.split(",")[7], state_broadcast_data.get(x.split(",")[7], "Unknown")))

#print data

for row in data.collect():
    print(row)