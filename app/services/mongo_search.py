
from    pymongo import MongoClient
import  os

# ----------------------------------------------------------------------------------------------- #
# Connect to MongoDB Atlas cluster
# ----------------------------------------------------------------------------------------------- #

MONGO_URI   = os.environ.get("MONGODB_URI")
client      = MongoClient(MONGO_URI)

# ----------------------------------------------------------------------------------------------- #
# Select the database and collection of the AI Act embedded documents
# ----------------------------------------------------------------------------------------------- #

db          = client["chatbot"]
collection  = db["aiact"]

# ----------------------------------------------------------------------------------------------- #
# Runs an Atlas Search for 'query' in the 'text' field (using a custom or default index),
# then merges all 'text' fields from the returned documents into a single string.
# ----------------------------------------------------------------------------------------------- #

def search_and_combine_text(query):

    pipeline = [
        {
            "$search": {
                "index": "aiact_index",  
                "text": {
                    "query": query,
                    "path": "text"
                }
            }
        },
        {
            "$limit": 2  # number of pages of the aiact we want to fetch
        }
    ]
    
    # ------------------------------------------------------------------------------------------- #
    # Get the results from Atlas Search
    # ------------------------------------------------------------------------------------------- #
    results = list(collection.aggregate(pipeline))
    
    # ------------------------------------------------------------------------------------------- #
    # Sort results by chunk_index
    # ------------------------------------------------------------------------------------------- #

    results = sorted(results, key=lambda doc: doc["chunk_index"])
    
    # ------------------------------------------------------------------------------------------- #
    # Combine all 'text' fields into one big string
    # ------------------------------------------------------------------------------------------- #

    combined_text = "\n\n".join(doc["text"] for doc in results)
    
    return combined_text