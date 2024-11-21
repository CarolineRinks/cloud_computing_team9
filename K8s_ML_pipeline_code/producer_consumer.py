import time
import os
import json
from kafka import KafkaConsumer

# Kafka configurations
result_topic_name = 'prediction_results'
bootstrap_server = "kafka-svc:30092"
group_id = os.getenv("POD_NAME", "default-consumer-group")

# Set up the consumer
consumer = KafkaConsumer(
    result_topic_name,
    bootstrap_servers=bootstrap_server,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=group_id,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Kafka consumer created and connected. Listening for messages...",flush=True)

# Process messages as they arrive
with open("latencies.txt", "w") as f:
    for msg in consumer:
        data = msg.value
        print("received data from inference server: ", data,flush=True)
        unique_id = data.get('ID')
        start_time=data.get('StartTime')
        print("Start time: ", start_time,flush=True)
        latency = time.time() - start_time
        print(f"Message ID: {unique_id}, Latency: {latency:.3f} seconds",flush=True)

        # Save latency value to file
        f.write(f"{latency}\n")
