class SummaryManager:
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage

    async def process_summaries(self):
        summaries = self.storage.get_messages_summary()
        for h in summaries:
            print(f'summary h: {h}')
            await self.send_message_to_channel(self, h.Server, h.Channel, h.Messages)

    async def send_message_to_channel(self, guild_id, channel_id, message_content):
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            print(f"Nie znaleziono serwera o ID: {guild_id}")
            return

        channel = guild.get_channel(channel_id)
        if channel is None:
            print(f"Nie znaleziono kanału o ID: {channel_id} w serwerze {guild.name}")
            return

        await channel.send(message_content)
        print(f"Wysłano wiadomość do kanału {channel.name} w serwerze {guild.name}")
