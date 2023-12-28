import os
from pymongo import MongoClient
import uuid
from datetime import datetime

class Storage:
    def __init__(self):
        mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongodb_url)
        self.db = self.client.memorittap
        self.messages_collection = self.db.messages

    def insert_message(self, author_id, text, channel_id, channel_name, guild_id):
        document = {
            "uuid": str(uuid.uuid4()),
            "author_id": author_id,
            "text": text,
            "timestamp": datetime.utcnow(),
            "modified": False,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "guild_id": guild_id
        }
        self.messages_collection.insert_one(document)

    def update_message(self, message_id, new_text, channel_id, channel_name, guild_id):
        self.messages_collection.update_one(
            {"uuid": message_id},
            {"$set": {
                "text": new_text, 
                "modified": True, 
                "channel_id": channel_id, 
                "channel_name": channel_name, 
                "guild_id": guild_id
            }}
        )

