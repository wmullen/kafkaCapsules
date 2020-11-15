#!/bin/bash

docker run --net=host -d \
    -e ZOOKEEPER_CLIENT_PORT=2181 \
    confluentinc/cp-zookeeper
sleep 5
docker run --net=host -d \
    -e KAFKA_ZOOKEEPER_CONNECT=127.0.0.1:2181 \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
    -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
    confluentinc/cp-kafka
