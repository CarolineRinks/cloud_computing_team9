#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import threading
from kafka import KafkaConsumer  # Consumer of events
import base64
from io import BytesIO
from PIL import Image
from pymongo import MongoClient
import os  # Import the os module

# Replace with your Kafka broker's IP and port
#bootstrap_servers = 'kafka-svc:30092'
bootstrap_servers = 'kafka-svc:30092'

# Replace with the topic names used in your producer and inference producer
db_topic_name = 'cifar'
inference_topic_name = 'inference'
# Replace these with your actual credentials
username = "root"
password = "example"
database_name = "cifarDatabase"

client = MongoClient('mongodb://mongodb:27017/')

# Access the database
db = client['cifarDatabase']

# Access the collection
collection = db['myCollection']

# Create a new directory for images if it doesn't exist
image_folder = 'image_folder'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Function to handle saving images and inserting into the database
def handle_db_consumer_message(data):
    # Insert the document into MongoDB
    result = collection.insert_one(data)
    print(f"Inserted document with _id: {result.inserted_id}")

    # Extract the fields
    unique_id = data.get('ID')
    producer_id=data.get('ProducerID')
    ground_truth = data.get('GroundTruth')
    img_base64 = data.get('Data')


# Function to handle inference data and update the MongoDB document
def handle_inference_consumer_message(data):
    # Extract the fields
    unique_id = data.get('ID')
    # producer_id=data.get('ProducerID')
    prediction = data.get('InferredValue')

    # Find the document with the matching ID and update it with the predicted label
    result = collection.update_one(
        {'ID': unique_id},  # Filter by unique ID and producer ID
        {'$set': {'InferredValue': prediction}}  # Set the prediction
    )
    
    print("prediction data", prediction)
    if result.modified_count > 0:
        print(f"Updated document with unique ID: {unique_id} with prediction: {prediction}")
    else:
        print(f"No document found with ID: {unique_id} to update.")

# Consumer thread for IoT (db_consumer) messages
def consume_db_messages():
    # Initialize the Kafka consumer
    db_consumer = KafkaConsumer(
        db_topic_name,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='db2-consumer-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # Deserialize JSON messages
    )
    
    print("DB Consumer is listening for messages...")
    
    try:
        for msg in db_consumer:
            print("iot data", msg)
            handle_db_consumer_message(msg.value)
    except KeyboardInterrupt:
        print("DB Consumer stopped.")
    finally:
        db_consumer.close()

# Consumer thread for inference messages
def consume_inference_messages():
    # Initialize the Kafka consumer
    inference_consumer = KafkaConsumer(
        inference_topic_name,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='inference2-consumer-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # Deserialize JSON messages
    )

    print("Inference Consumer is listening for messages...")
    
    try:
        for msg in inference_consumer:
            print("inference data", msg)
            handle_inference_consumer_message(msg.value)
    except KeyboardInterrupt:
        print("Inference Consumer stopped.")
    finally:
        inference_consumer.close()

# Run the consumers concurrently using threading
if __name__ == "__main__":
# Create a thread for the db consumer
    # Create threads for each consumer
    db_thread = threading.Thread(target=consume_db_messages)
    inference_thread = threading.Thread(target=consume_inference_messages)

    # Start both threads
    db_thread.start()
    inference_thread.start()

    # Wait for both threads to finish
    db_thread.join()
    inference_thread.join()

    # Close MongoDB client
    client.close()
