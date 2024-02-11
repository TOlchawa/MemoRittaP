class ConfigurationHelper:
    def __init__(self, storage):
        self.storage = storage

    def is_channel_listened(self, guild_id, channel_name):
        listened_channels = self.storage.get_listened_channels(guild_id)
        str_guild_id=str(guild_id)
        channels=listened_channels.get(str_guild_id, [])
        result = channel_name in channels
        return result