#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Your Name
Course: CS4287-5287: Principles of Cloud Computing, Vanderbilt University
Purpose:
    Simple Kafka Consumer for Testing.
    This script connects to a Kafka broker, subscribes to the specified topic,
    consumes JSON messages, and prints out the 'ID' and 'GroundTruth' fields.
"""

import json
from kafka import KafkaConsumer  # Consumer of events
import base64
from io import BytesIO
from PIL import Image,ImageFilter
# Replace with your Kafka broker's IP and port
bootstrap_servers = '192.168.5.224:9092'

# Replace with the topic name you used in your producer
topic_name = 'cifar'

# Initialize the Kafka consumer
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',  # Start reading from the earliest message
    enable_auto_commit=True,
    group_id='simple-consumer-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # Deserialize JSON messages
)

print("Consumer is listening for messages...")

# Process messages as they arrive
try:
    for msg in consumer:
        # The message value is already deserialized into a Python dict
        print("msg: ",msg)

        data = msg.value

        print("data ",data)

        # Extract the fields
        unique_id = data.get('ID')
        ground_truth = data.get('GroundTruth')
        img_base64=data.get('Data')

        # Print the basic information
        print(f"Received message with ID: {unique_id}, GroundTruth: {ground_truth}")
        # Optionally, decode and save the image
        img_bytes = base64.b64decode(img_base64)
        image = Image.open(BytesIO(img_bytes))
        image_filename = f"{unique_id}_{ground_truth}.png"
        image.save(image_filename)
        print(f"Image saved as {image_filename}")

        # You can add additional prints or processing here if needed

except KeyboardInterrupt:
    print("Consumer stopped.")
finally:
    # Close the consumer gracefully
    consumer.close()

