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
        self.config_collection = self.db.config


    def insert_message(self, author_id, text, channel_id, channel_name, guild_id, direct_message):
        document = {
            "uuid": str(uuid.uuid4()),
            "author_id": author_id,
            "text": text,
            "timestamp": datetime.utcnow(),
            "modified": False,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "guild_id": guild_id,
            "direct_message": direct_message
        }
        self.messages_collection.insert_one(document)

    def update_message(self, message_id, new_text, channel_id, channel_name, guild_id, direct_message):
        self.messages_collection.update_one(
            {"uuid": message_id},
            {"$set": {
                "text": new_text, 
                "modified": True, 
                "channel_id": channel_id, 
                "channel_name": channel_name, 
                "guild_id": guild_id,
                "direct_message": direct_message
            }}
        )
        
    def is_user_authorized(self, user_id):
        config = self.config_collection.find_one({"config_type": "authorized_users"})
        if config and "users" in config:
            return str(user_id) in config["users"]
        return False

    def add_authorized_user(self, user_id):
        self.config_collection.update_one(
            {"config_type": "authorized_users"},
            {"$addToSet": {"users": str(user_id)}},
            upsert=True
        )


    def get_messages_summary(self):
        summaries = []

        # Aggregation pipeline to group messages by server and channel
        pipeline = [
            {"$group": {
                "_id": {"guild_id": "$guild_id", "channel_id": "$channel_id", "channel_name": "$channel_name"},
                "message_count": {"$sum": 1}
            }}
        ]
        results = self.messages_collection.aggregate(pipeline)

        for result in results:
            guild_id = result["_id"]["guild_id"]
            channel_id = result["_id"]["channel_id"]
            channel_name = result["_id"]["channel_name"]
            message_count = result["message_count"]

            header = f"Server: {guild_id}, Channel: {channel_name} ({channel_id}), Messages: {message_count}"
            summaries.append(header)

        print(f"summaries: {summaries}", flush=True)
        return summaries

    def get_listened_channels(self):
        config = self.config_collection.find_one({"config_type": "listened_channels"})
        return config.get("channels", {}) if config else {}
        
    def add_listened_channel(self, guild_id, channel_name):
        self.config_collection.update_one(
            {"config_type": "listened_channels"},
            {"$addToSet": {"channels." + str(guild_id): channel_name}},
            upsert=True
        )

    def close(self):
        print(f"Closing storage ...", flush=True)
        self.client.close()