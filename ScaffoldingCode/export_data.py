from pymongo import MongoClient
import json
import time

# Replace 'localhost' with the service name 'mongodb' and use the default MongoDB port
client = MongoClient('mongodb://mongodb:27017/')
db = client['cifarDatabase']

# Example: Fetch and print all documents from a collection
collection = db['myCollection']
#for document in collection.find():
#    print("document",document)
cursor = collection.find({}, {'ProducerID': 1, 'GroundTruth': 1, 'InferredValue': 1, '_id': 0})
data = list(cursor)
#print("data",data)
# Save data to a file (optional)
with open('db_data.json', 'w') as file:
    json.dump(data, file)

while True:
    time.sleep(10000)


