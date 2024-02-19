class SummaryManager:
    def __init__(self, bot, storage, openai_helper):
        self.bot = bot
        self.storage = storage
        self.openai_helper = openai_helper
        self.min_number_of_messages = 10
        self.min_total_len_messages = 100

    async def process_summaries(self):
        summaries = self.storage.get_messages_summary()
        print(f"summaries: {summaries}", flush=True)
        for h in summaries:
            print(f'summary h: {h}')
            g_id = h["guild_id"]
            print(f'summary h["guild_id"]: {g_id}')

            message_sum_len = 0
            for s in h["message_list"]:
                message_sum_len += len(s)
            message_count = len(h["message_list"])

            if message_count >= self.min_number_of_messages and message_sum_len >= self.min_total_len_messages:
                final_summary = await self.openai_helper.summarize_messages(h["message_list"])
                self.storage.remove_messages(summaries)
                await self.send_message_to_channel(h["guild_id"], h["channel_id"], final_summary)

    async def send_message_to_channel(self, str_guild_id, str_channel_id, message_content):
        guild_id = int(str_guild_id)
        channel_id = int(str_channel_id)
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            print(f"server not found: {guild_id}")
            return

        channel = guild.get_channel(channel_id)
        if channel is None:
            print(f"channel not found: {channel_id} server {guild.name}")
            return

        await channel.send(message_content)
        print(f"message sent; channel: {channel.name} server: {guild.name}")
