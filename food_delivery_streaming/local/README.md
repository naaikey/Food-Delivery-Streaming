## Food Delivery Streaming Pipeline

This project implements a real-time data pipeline for food delivery orders using PostgreSQL, Kafka, and Spark Structured Streaming. The pipeline extracts order data from PostgreSQL, streams it to Kafka, and writes it to a Parquet data lake with deduplication and partitioning.

## Architecture

PostgreSQL (Source) -> Python CDC Producer -> Kafka Topic -> Spark Structured Streaming -> Data Lake (Parquet)

- PostgreSQL: Source database for order data.
- Kafka: Message broker for streaming order data.
- Spark Structured Streaming: Processes Kafka messages and writes to Parquet.
- Data Lake: Parquet files partitioned by date.

## Prerequisites

Ensure the following services are installed and running locally:

1.  **PostgreSQL** (Port 5432)
2.  **Apache Kafka** (Port 9092)
3.  **Apache Spark** (Version 3.5.1 recommended)
4.  **Python 3.9+** with kafka-python and psycopg2-binary installed.

## Project Structure

1100378/
└── food_delivery_streaming/
    └── local/
        ├── db/
        │   └── orders.sql            
        ├── producers/
        │   └── orders_cdc_producer.py 
        ├── consumers/
        │   └── orders_stream_consumer.py 
        ├── scripts/
        │   ├── producer_spark_submit.sh  
        │   └── consumer_spark_submit.sh  
        ├── configs/
        │   └── orders_stream.yml      
        └── README.md

## Setup

### Linux/macOS

1. Start ZooKeeper and Kafka:
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties

2. Start Producer: This script polls the database and pushes new records to Kafka.
export PYSPARK_PYTHON=python3

spark-submit
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3
producers/orders_cdc_producer.py
--config configs/orders_stream.yml

bash scripts/producer_spark_submit.sh

3. Start Consumer: Open a new terminal to start the Spark Streaming job.
export PYSPARK_PYTHON=python3

spark-submit
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3
consumers/orders_stream_consumer.py
--config configs/orders_stream.yml

bash scripts/consumer_spark_submit.sh

### Windows

- Replace `.sh` with `.bat` for ZooKeeper and Kafka.
- Use `set PYSPARK_PYTHON=python` instead of `export`.

## Testing

### Insert Records in PostgreSQL

Connect to the database and insert records:
psql -h localhost -U student -d food_delivery_db

Insert base records:
INSERT INTO orders_1100378 (customer_name, restaurant_name, item, amount, order_status, created_at)
VALUES ('Test User', 'Test Dhaba', 'Pav Bhaji', 180.00, 'PLACED', NOW());

Insert incremental records:
INSERT INTO orders_1100378 (customer_name, restaurant_name, item, amount, order_status, created_at) VALUES
('Increment A1', 'Test Dhaba', 'Pav Bhaji', 180.00, 'PLACED', NOW()),
('Increment A2', 'Test Dhaba', 'Masala Dosa', 150.00, 'PLACED', NOW()),
('Increment A3', 'Test Dhaba', 'Idli', 90.00, 'PREPARING', NOW()),
('Increment A4', 'Test Dhaba', 'Chole Bhature', 220.00, 'DELIVERED', NOW()),
('Increment A5', 'Test Dhaba', 'Veg Thali', 300.00, 'PLACED', NOW());

Repeat for the second batch.

### Validate Results

- Check for duplicates:
SELECT order_id, COUNT(*) FROM orders_1100378 GROUP BY order_id HAVING COUNT(*) > 1;

- Check Parquet output:
- Use a Spark script to read Parquet files and count rows and distinct order_id values.

To print all records from the orders_1100378 table in the terminal, use this SQL command in psql:
SELECT * FROM orders_1100378;

## Project Structure

- **local/**: Main project folder with all scripts and configuration files.
- **README.md**: Project documentation and setup instructions.
- **producers/**: Contains the CDC producer code (`orders_cdc_producer.py`) that polls PostgreSQL and sends new orders to Kafka.
- **consumers/**: Contains the Spark streaming consumer code (`orders_stream_consumer.py`) that reads from Kafka and writes Parquet files.
- **configs/**: Configuration files for the pipeline, including `orders_stream.yml`.
- **scripts/**: Bash scripts (`producer_spark_submit.sh`, `consumer_spark_submit.sh`) to start producer and consumer.
- **output/orders/**: Parquet data lake where consumer writes partitioned files by date.

