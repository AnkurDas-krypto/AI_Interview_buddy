from pymongo import MongoClient
import pymongo
from bson import ObjectId
import os


def download_pdf_from_mongo(pdf_id, local_file_path):
    # MongoDB connection parameters
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    DB_NAME = 'resume_saver'
    COLLECTION_NAME = 'applier_answers'

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Fetch the PDF by its ID
    pdf_data = collection.find_one({'_id': ObjectId(pdf_id)})

    if pdf_data:
        # Assuming the PDF data is stored in a field named 'pdf_file'
        with open(local_file_path, 'wb') as f:
            f.write(pdf_data['pdf_file'])
        print(f"PDF has been downloaded to {local_file_path}")
    else:
        print("PDF not found in the database.")

# Example usage
download_pdf_from_mongo('6658e55d5fa9cae832f467fc', 'test.pdf')
