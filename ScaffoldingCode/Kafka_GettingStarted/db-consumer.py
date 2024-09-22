#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from kafka import KafkaConsumer  # Consumer of events
import base64
from io import BytesIO
from PIL import Image,ImageFilter
from pymongo import MongoClient
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


# Connect to MongoDB on localhost (default port 27017)
client = MongoClient('mongodb://localhost:27017/')

# Access the database
db = client['cifarDatabase']

# Access the collection
collection = db['myCollection']

# Insert a document
#result = collection.insert_one({'name': 'Bob', 'age': 25})
#print(f"Inserted document with _id: {result.inserted_id}")

# Find a document
#document = collection.find_one({'name': 'Bob'})
#print("Found document:", document)

# Update a document

#collection.update_one({'name': 'Bob'}, {'$set': {'age': 26}})

# Delete a document
#collection.delete_one({'name': 'Bob'})

# Close the connection
#client.close()
# Process messages as they arrive
try:
    for msg in consumer:
        # The message value is already deserialized into a Python dict
        data = msg.value
        result = collection.insert_one(data)
        print(f"Inserted document with _id: {result.inserted_id}")

        # Extract the fields
        unique_id = data.get('ID')
        ground_truth = data.get('GroundTruth')
        img_base64=data.get('Data')

        # Print the basic information
        #print(f"Received message with ID: {unique_id}, GroundTruth: {ground_truth}")
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
    client.close()

