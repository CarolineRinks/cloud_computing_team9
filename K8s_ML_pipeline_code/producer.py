import os
import time
import numpy as np
import random
import uuid
import json
import base64
from io import BytesIO
from PIL import Image
from kafka import KafkaProducer
from tensorflow.keras.datasets import cifar10
import cv2

# Load CIFAR10 Dataset
(X_train, y_train), (X_test, y_test) = cifar10.load_data()
X_data = np.concatenate((X_train, X_test))
y_data = np.concatenate((y_train, y_test))
producer_id = os.getenv("POD_NAME", "default-producer")
print("Producer id is: ",producer_id,flush=True)
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

# Kafka configurations
topic_name = 'cifar'
bootstrap_server = "kafka-svc:30092"

# Set up the producer
producer = KafkaProducer(bootstrap_servers=bootstrap_server, acks=1)

# Send messages
for i in range(1000):
    idx = random.randint(0, len(X_data) - 1)
    image = X_data[idx]
    label_index = y_data[idx][0]
    label_name = cifar10_labels[label_index]

    # Prepare the image data
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    pil_image = Image.fromarray(blurred_image)
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    unique_id = str(uuid.uuid4())
    start_time=time.time()
    message = {
        'ID': unique_id,
        'ProducerID': producer_id,
        'GroundTruth': label_name,
        'Data': img_base64,
        'StartTime':start_time,
    }

    json_data = json.dumps(message)

    try:
        producer.send(topic_name, value=json_data.encode('utf-8'))
        producer.flush()
        print(f"Sent image ID {unique_id} with label {label_name}")
    except Exception as e:
        print(f"Error sending message: {e}")

    time.sleep(1)

# Close the producer
producer.close()
