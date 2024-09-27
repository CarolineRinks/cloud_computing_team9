# Fall 2024
# Principles of Cloud Computing: Team 9
# Code for the ML model -- also included in inference-consumer.py
# this file was used for testing.

import torch
import numpy as np
import json
from kafka import KafkaConsumer  # Consumer of events
import base64
from io import BytesIO
from PIL import Image, ImageFilter
from torchvision import transforms
# Kafka broker's IP and port
#bootstrap_servers = '192.168.5.224:9092'
inference_consumer = '192.168.5.149'

# set device to gpu if available, else cpu
gpu_avail = torch.cuda.is_available()
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# Download pre-trained ResNet18 model
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
model.to(device)
model.eval()
# Define label names for cifar dataset
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

# Replace with the topic name you used in your producer (inference consumer)
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
        #print("msg: ",msg)  # the message value is already deserialized into a Python dict
        data = msg.value
        #print("data ",data)

        # Extract the fields
        unique_id = data.get('ID')
        ground_truth = data.get('GroundTruth')
        img_base64 = data.get('Data')

        # Print the basic information
        print(f"Received message with ID: {unique_id}, GroundTruth: {ground_truth}")
        
        # Optionally, decode and save the image
        img_bytes = base64.b64decode(img_base64)
        input_image = Image.open(BytesIO(img_bytes))
        #image_filename = f"{unique_id}_{ground_truth}.png"
        #image.save(image_filename)
        #print(f"Image saved as {image_filename}")

        # PERFORM INFERENCE on the image received ---------------------------------

        # 1. Transform image for ResNet18

        # a. Resize original image
        resize = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
        ])
        resized_image = resize(input_image)
        preprocess = transforms.Compose([
            transforms.ToTensor(),
        ])
        preprocess_norm = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(resized_image)
        input_batch = input_tensor.unsqueeze(0)
        input_tensor_normalized = preprocess_norm(resized_image)
        input_batch_normalized = input_tensor_normalized.unsqueeze(0)
        # b. Move image to device
        input_batch = input_batch.to(device)
        input_batch_normalized = input_batch_normalized.to(device)
        
        # 2. Get the model's predictions on the image
        with torch.no_grad():
            output = model(input_batch) # Tensor of shape [1,1000], with confidence scores over ImageNet's 1000 classes
        probabilities = torch.nn.functional.softmax(output[0], dim=0)   # output is logits
        probabilities = probabilities.detach().cpu()

        # Get the category predicted by the model
        top_prob, top_id = torch.topk(probabilities, 1)

        print("Predicted Class: ", cifar10_labels[top_id], top_prob.item())


except KeyboardInterrupt:
    print("Consumer stopped.")
finally:
    # Close the consumer gracefully
    consumer.close()
