from pymongo import MongoClient, errors
import json
from datetime import datetime

mongo_user = "user"
mongo_password = "user"
mongo_db = "Transparency"
mongo_collection_load = "Load"
mongo_collection_prices = "Prices"
mongo_collection_production = "Production"

# MongoDB connection parameters
client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@127.0.0.1:27117,127.0.0.1:27118/?authMechanism=DEFAULT")

# Input data file (JSON format)
data_load = "../import/Transparency.Load.json"
data_prices = "../import/Transparency.Prices.json"
data_production = "../import/Transparency.Production.json"

# Access the target database and collection
db = client[mongo_db]

# Function to import data from JSON file into MongoDB
def import_data(data_file, collection):
    collection = db[collection]
    with open(data_file, "r") as file:
        data = json.load(file)

    # If data is in a list of documents, you can insert many at once
    try:
        print(f"Starting import of {len(data)} documents...")
        start_time = datetime.now()

        # Insert data into the collection
        result = collection.insert_many(data)  # Use insert_one for individual documents

        # Print number of inserted documents
        print(f"Inserted {len(result.inserted_ids)} documents.")
        end_time = datetime.now()
        print(f"Data import completed in {end_time - start_time}")

    except errors.PyMongoError as e:
        print(f"Error occurred during import: {e}")
        raise


# Run the import
if __name__ == "__main__":
    import_data(data_load, mongo_collection_load)
    import_data(data_prices, mongo_collection_prices)
    import_data(data_production, mongo_collection_production)
