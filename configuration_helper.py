class ConfigurationHelper:
    def __init__(self, storage):
        self.storage = storage

    def is_channel_listened(self, guild_id, channel_name):
        listened_channels = self.storage.get_listened_channels(guild_id)
        return channel_name in listened_channels
