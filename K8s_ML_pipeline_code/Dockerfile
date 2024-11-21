# Docker file to for producer container
# The FROM clause tells docker what underlying base to use.
FROM python:3.10
RUN apt-get update && apt-get install -y libgl1-mesa-glx
# Install the application dependencies
#WORKDIR /root/cloud_computing_team9/ScaffoldingCode
# Copy the application dependencies file to the current directory
COPY requirements.txt .
# Install the application dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the producer code to the current directory
COPY producer.py .
# Run the server code as the final step of starting the container
CMD ["python3", "producer.py"]
