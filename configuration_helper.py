class ConfigurationHelper:
    def __init__(self, storage):
        self.storage = storage

    def is_channel_listened(self, guild_id, channel_name):
        listened_channels = self.storage.get_listened_channels()
        result = channel_name in listened_channels.get(str(guild_id), [])
        #print(f'{channel_name} looking for {listened_channels} and result is: {result}')
        return result