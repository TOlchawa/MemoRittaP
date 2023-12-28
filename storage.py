import os
from pymongo import MongoClient

class Storage:
    def __init__(self):
        mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongodb_url)
        self.db = self.client.memorittap
        self.collection = self.db.notes

    def insert_document(self, document):
        self.collection.insert_one(document)

    def find_document(self, query):
        return self.collection.find_one(query)