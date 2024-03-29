import json
import os
import uuid
from datetime import datetime

from pymongo import MongoClient


class Storage:
    def __init__(self):
        mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        print(f"mongodb_url: {mongodb_url}")
        self.client = MongoClient(mongodb_url)
        self.db = self.client.memorittap
        self.messages_collection = self.db.messages
        self.config_collection = self.db.config

    def insert_message(self, author_id, author_name, text, channel_id, channel_name, guild_id, direct_message):
        document = {
            "uuid": str(uuid.uuid4()),
            "author_id": author_id,
            "author_name": author_name,
            "text": "'" + author_name + "' said: " + text,
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

        # Aggregation pipeline to group messages by server and channel and collect message texts
        pipeline = [
            {"$group": {
                "_id": {"guild_id": "$guild_id", "channel_id": "$channel_id", "channel_name": "$channel_name"},
                "message_count": {"$sum": 1},
                "messages": {"$push": "$text"}  # Zmiana z "$direct_message" na "$text"
            }}
        ]
        results = self.messages_collection.aggregate(pipeline)

        for result in results:
            guild_id = result["_id"]["guild_id"]
            channel_id = result["_id"]["channel_id"]
            channel_name = result["_id"]["channel_name"]
            message_count = result["message_count"]
            messages = result["messages"]  # This is your list of message texts

            summaries.append({
                "guild_id": guild_id,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "message_count": message_count,
                "message_list": messages  # Dodano listę treści wiadomości tutaj
            })

        print(f"summaries: {summaries}", flush=True)
        return summaries

    def remove_messages(self, summaries):
        # remove all records from 'summaries' greated in get_messages_summary(self)
        for summary in summaries:
            # Extract guild_id and channel_id from the summary
            guild_id = summary['guild_id']
            channel_id = summary['channel_id']

            # Build a query to match messages belonging to the specific guild_id and channel_id
            query = {"guild_id": guild_id, "channel_id": channel_id}

            # Execute the delete operation on the messages_collection
            result = self.messages_collection.delete_many(query)

            # Optionally, you can print the result of the delete operation
            print(f"Removed {result.deleted_count} messages from guild {guild_id}, channel {channel_id}", flush=True)

    def get_listened_channels(self, guild_id):
        config = self.config_collection.find_one({"guild_id": str(guild_id), "config_type": "listened_channels"})
        return config.get("channels", {}) if config else {}

    def getconfig(self, guild_id):
        # config = self.config_collection.find_one({"guild_id": guild_id})
        # return config.get("channels", {}) if config else {}
        configuration = self.config_collection.find_one({'guild_id': guild_id})
        if '_id' in configuration:
            del configuration['_id']
        if 'guild_id' in configuration:
            del configuration['guild_id']
        json_data = json.dumps(configuration, default=str)
        print(f"configuration for {guild_id}: {configuration}")
        return json_data

    def add_listened_channel(self, guild_id, channel_name):
        result = self.config_collection.update_one(
            {"guild_id": guild_id, "config_type": "listened_channels"},
            {"$addToSet": {"channels": channel_name}},
            upsert=True
        )
        print(f"add_listened_channel modified_count: {result.modified_count}")
        return result

    def remove_listened_channel(self, guild_id, channel_name):
        result = self.config_collection.update_one(
            {"guild_id": guild_id, "config_type": "listened_channels"},
            {"$pull": {"channels": channel_name}}
        )
        print(f"remove_listened_channel modified_count: {result.modified_count}")
        return result

    def close(self):
        print(f"Closing storage ...", flush=True)
        self.client.close()
