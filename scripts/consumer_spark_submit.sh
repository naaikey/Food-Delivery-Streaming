#!/bin/bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3 consumers/orders_stream_consumer.py --config configs/orders_stream.yml
