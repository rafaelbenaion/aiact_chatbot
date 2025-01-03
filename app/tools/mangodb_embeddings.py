import json
import os
from   pymongo import MongoClient

# ----------------------------------------------------------------------------------------------- #
# MongoDB connection string (modify if needed for your setup)
# ----------------------------------------------------------------------------------------------- #

mongo_uri   = os.environ.get("MONGODB_URI")
client      = MongoClient(mongo_uri)

# ----------------------------------------------------------------------------------------------- #
# Database and collection
# ----------------------------------------------------------------------------------------------- #

db          = client["chatbot"]
collection  = db["aiact"]

# ----------------------------------------------------------------------------------------------- #
# Path to the JSON file containing embeddings
# ----------------------------------------------------------------------------------------------- #

json_file_path = "app/tools/page_embeddings.json"

# ----------------------------------------------------------------------------------------------- #
# Load the JSON data
# ----------------------------------------------------------------------------------------------- #

with open(json_file_path, "r") as f:
    data = json.load(f)

# ----------------------------------------------------------------------------------------------- #
# Insert data into MongoDB collection
# ----------------------------------------------------------------------------------------------- #

result = collection.insert_many(data)

print(f"Inserted {len(result.inserted_ids)} documents into MongoDB collection.")
