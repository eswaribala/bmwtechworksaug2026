#step1 
from pyspark.sql import SparkSession

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
jdbc_url = "jdbc:postgresql://localhost:5432/your_database"  #
