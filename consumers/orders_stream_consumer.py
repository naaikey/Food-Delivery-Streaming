import argparse
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, date_format
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType

# Load YAML configuration file
def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Main Spark Structured Streaming consumer function
def run_consumer(config_path):
    config = load_config(config_path)

    # Create SparkSession with checkpointing config for exactly-once stream processing
    spark = SparkSession.builder \
        .appName("FoodDeliveryStreaming") \
        .config("spark.sql.streaming.checkpointLocation", config['streaming']['checkpoint_location']) \
        .getOrCreate()

    # Reduce logging noise
    spark.sparkContext.setLogLevel("WARN")

    # Define schema to parse incoming JSON order events
    schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("customer_name", StringType(), True),
        StructField("restaurant_name", StringType(), True),
        StructField("item", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("order_status", StringType(), True),
        StructField("created_at", StringType(), True)
    ])

    # Read streaming data from Kafka topic
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", config['kafka']['brokers']) \
        .option("subscribe", config['kafka']['topic']) \
        .option("startingOffsets", "earliest") \
        .load()

    # Extract 'value' from Kafka and parse JSON according to schema
    orders_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    # Data cleaning: filter out records with null order_id or negative amount
    cleaned_df = orders_df.filter(
        col("order_id").isNotNull() &
        (col("amount") >= 0)
    ).dropDuplicates(["order_id"]).withColumn("created_at", col("created_at").cast(TimestampType()))

    # Add date partition column formatted as yyyy-MM-dd derived from created_at timestamp
    final_df = cleaned_df.withColumn("date", date_format(col("created_at"), "yyyy-MM-dd"))

    # Write the streaming data to data lake with specified format and partitioning
    query = final_df.writeStream \
        .format(config['datalake']['format']) \
        .outputMode("append") \
        .partitionBy("date") \
        .option("path", config['datalake']['path']) \
        .option("checkpointLocation", config['streaming']['checkpoint_location']) \
        .start()

    print("Spark Streaming Job Started with Deduplication...")
    # Await termination to keep the streaming query running continuously
    query.awaitTermination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config file")
    args = parser.parse_args()
    run_consumer(args.config)