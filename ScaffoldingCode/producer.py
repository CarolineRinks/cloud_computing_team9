#
#
#
# Author: Team 9
# CS4287-5287: Principles of Cloud Computing, Vanderbilt University
#
# Created: Sept 2024
#
# Purpose:
#
#    Provides the logic for the IoT source producer in Assignment 1.
#

import os
import time
from kafka import KafkaProducer  # producer of events

import os
import time
import numpy as np
import random
import uuid
import json
import base64
from io import BytesIO
from PIL import Image, ImageFilter
from kafka import KafkaProducer
from tensorflow.keras.datasets import cifar10
import cv2

# Load the CIFAR10 Dataset
(X_train, y_train), (X_test, y_test) = cifar10.load_data()
X_data = np.concatenate((X_train, X_test))
y_data = np.concatenate((y_train, y_test))
# Define label names for ground truth
cifar10_labels = {
    0: 'airplane',
    1: 'automobile',
    2: 'bird',
    3: 'cat',
    4: 'deer',
    5: 'dog',
    6: 'frog',
    7: 'horse',
    8: 'ship',
    9: 'truck'
}


# acquire the producer
bootstrap_servers = 'kafka-svc.default.svc.cluster.local:9092'
producer = KafkaProducer (bootstrap_servers=bootstrap_servers, 
                                          acks=1)  # wait for leader to write to log

for i in range (100):
    
    # Randomly select an image from the dataset
    idx = random.randint(0, len(X_data) - 1)
    image = X_data[idx]
    label_index = y_data[idx][0]
    label_name = cifar10_labels[label_index]
   
    # (Optional): Save the image for verification purposes
    # Convert the NumPy array to a PIL Image
    og_image = Image.fromarray(image)
    og_image.save("og_image_1.png")

    # Add blurriness to the image using Gaussian blur
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    blurred_image_tmp = Image.fromarray(blurred_image)
    blurred_image_tmp.save("blurred_image_1.png")

    # Convert the blurred image to bytes
    pil_image = Image.fromarray(blurred_image)
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    # Generate a unique ID for the message
    unique_id = str(uuid.uuid4())
    
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
    






