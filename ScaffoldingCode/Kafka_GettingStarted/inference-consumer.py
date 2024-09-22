# Fall 2024
# Principles of Cloud Computing: Team 9
# Code for the inference consumer

import torch
import numpy as np
import json
from kafka import KafkaConsumer  # Consumer of events
import base64
from io import BytesIO
from PIL import Image,ImageFilter
# Kafka broker's IP and port
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
        img_base64 = data.get('Data')

        # Print the basic information
        print(f"Received message with ID: {unique_id}, GroundTruth: {ground_truth}")
        # Optionally, decode and save the image
        img_bytes = base64.b64decode(img_base64)
        image = Image.open(BytesIO(img_bytes))
        image_filename = f"{unique_id}_{ground_truth}.png"
        image.save(image_filename)
        print(f"Image saved as {image_filename}")

        # You can add additional prints or processing here if needed
        # SENDING DATA RECEIVED FROM BROKER TO ml-model.py
        producer = KafkaProducer (bootstrap_servers="192.168.5.224:9092",
                                          acks=1)  # wait for leader to write to log

        # Prepare the JSON message
        message = {
            'ID': unique_id,
            'GroundTruth': label_name,
            'Data': img_base64
        }

        json_data = json.dumps(message)

        try:
            producer.send('cifar', value=bytes (json_data, 'ascii'))  # Replace with your actual topic name
            producer.flush()
            print(f"Sent image ID {unique_id} with label {label_name}")
        except Exception as e:
            print(f"Error sending message: {e}")
            print(e)

        # sleep a second
        time.sleep (1)

    # we are done
    producer.close ()



except KeyboardInterrupt:
    print("Consumer stopped.")
finally:
    # Close the consumer gracefully
    consumer.close()
