#step1 
from pyspark.sql import SparkSession
from pysparkmodule.configurations.config import Config
#create driver
spark = (
        SparkSession.builder
        .appName("Spark PostgreSQL Example")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.2.18")  # Path to the PostgreSQL JDBC driver
        #cluster mode
        .master("local[*]")  # Use local mode for testing; adjust as needed for your cluster
        .getOrCreate()
      )
#create jdbc url
jdbc_url = Config().get_jdbc_connection_string()

result=spark.read.jdbc(url=jdbc_url, 
                table="vehicle", 
                properties=Config().get_db_connection_params())

print("Data read from PostgreSQL:")
result.show()
