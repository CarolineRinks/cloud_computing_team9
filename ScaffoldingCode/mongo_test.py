from pymongo import MongoClient

# Connect to MongoDB on localhost (default port 27017)
client = MongoClient('mongodb://localhost:27017/')

# Access the database
db = client['myDatabase']

# Access the collection
collection = db['myCollection']

# Insert a document
result = collection.insert_one({'name': 'Bob', 'age': 25})
print(f"Inserted document with _id: {result.inserted_id}")

# Find a document
document = collection.find_one({'name': 'Bob'})
print("Found document:", document)

# Update a document
collection.update_one({'name': 'Bob'}, {'$set': {'age': 26}})

# Delete a document
#collection.delete_one({'name': 'Bob'})

# Close the connection
client.close()

