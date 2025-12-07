import time
import json
import yaml
import argparse
import psycopg2
import os
from kafka import KafkaProducer
from datetime import datetime, date
from decimal import Decimal

# Custom JSON serializer to handle datetime and Decimal types
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# Load YAML configuration file
def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Retrieve last processed timestamp from state file to avoid duplicate processing
def get_last_processed_timestamp(state_file):
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            data = json.load(f)
            return data.get('last_processed_timestamp', '1970-01-01 00:00:00')
    return '1970-01-01 00:00:00'  # Default timestamp if state file not found

# Update last processed timestamp after successful processing
def update_last_processed_timestamp(state_file, timestamp):
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump({'last_processed_timestamp': str(timestamp)}, f)

# Main CDC producer function to poll Postgres and send new entries to Kafka
def run_producer(config_path):
    config = load_config(config_path)
    # Create Kafka producer with JSON serialization
    producer = KafkaProducer(
        bootstrap_servers=config['kafka']['brokers'],
        value_serializer=lambda v: json.dumps(v, default=json_serializer).encode('utf-8')
    )
    topic = config['kafka']['topic']
    pg_conf = config['postgres']

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host=pg_conf['host'],
        port=pg_conf['port'],
        database=pg_conf['db'],
        user=pg_conf['user'],
        password=pg_conf['password']
    )
    state_file = config['streaming']['last_processed_timestamp_location']

    print(f"Starting CDC Producer... Topic: {topic}")

    while True:
        # Read the last processed timestamp to fetch only new records
        last_ts = get_last_processed_timestamp(state_file)
        print(f"Polling for new records after: {last_ts}")

        cur = conn.cursor()
        # Query to detect new rows inserted after last processed timestamp
        query = f"SELECT * FROM {pg_conf['table']} WHERE created_at > '{last_ts}' ORDER BY created_at ASC"
        cur.execute(query)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]

        if rows:
            print(f"Found {len(rows)} new records.")
            max_ts = last_ts
            for row in rows:
                # Convert each new row into a dictionary representing JSON
                record = dict(zip(column_names, row))
                # Publish JSON record to Kafka topic
                producer.send(topic, record)
                print(f"Sent order_id: {record['order_id']}")
                # Track the maximum created_at timestamp processed
                if str(record['created_at']) > str(max_ts):
                    max_ts = record['created_at']
            producer.flush()
            # Update last processed timestamp after sending all records
            update_last_processed_timestamp(state_file, max_ts)
        else:
            print("No new records found.")

        cur.close()
        # Pause for configured interval before polling again
        time.sleep(config['streaming']['batch_interval'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config file")
    args = parser.parse_args()
    run_producer(args.config)
