import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
class MongoDBClient:
    def __init__(self, uri=None, db_name=None):
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        
        self.db_name = db_name or os.getenv('MONGODB_DB', 'shield')
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def client(self):
        return self.client

    def close(self):
        self.client.close()
