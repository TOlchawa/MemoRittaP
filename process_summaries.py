class SummaryManager:
    def __init__(self, bot, storage, openai_helper):
        self.bot = bot
        self.storage = storage
        self.openai_helper = openai_helper

    async def process_summaries(self):
        summaries = self.storage.get_messages_summary()
        print(f"summaries: {summaries}", flush=True)
        for h in summaries:
            print(f'summary h: {h}')
            g_id = h["guild_id"]
            print(f'summary h["guild_id"]: {g_id}')

            final_summary = await self.openai_helper.summarize_messages(h["message_list"])
            print(final_summary)

            await self.send_message_to_channel(h["guild_id"], h["channel_id"], final_summary)

    async def send_message_to_channel(self, str_guild_id, str_channel_id, message_content):
        guild_id=int(str_guild_id)
        channel_id=int(str_channel_id)
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
