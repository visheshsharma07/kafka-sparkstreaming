from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Create Spark session
spark = SparkSession.builder \
    .appName("Kafka to Parquet Streaming") \
    .getOrCreate()

# Define the schema for the incoming JSON data
schema = StructType([
    StructField("number", IntegerType(), True)  # Adjust this schema based on your JSON structure
])

# Read streaming data from Kafka
kafka_df = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "random_number_topic")
    .load())

# Extract the value column as JSON and apply the schema
json_df = (kafka_df.selectExpr("CAST(value AS STRING) AS json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*"))

# Write the streaming DataFrame to Parquet files
query = (json_df.writeStream
    .format("parquet")
    .option("path", "./streaming_data")  # Set your output directory
    .option("checkpointLocation", "./streaming_data/checkpoint")  # Set your checkpoint directory
    .outputMode("append")
    .start())

# Await termination of the query
query.awaitTermination()