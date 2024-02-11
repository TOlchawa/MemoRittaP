import discord
import os
import asyncio
from discord.ext import commands
from storage import Storage
from openai_helper import OpenAIHelper
from process_summaries import SummaryManager
from configuration_helper import ConfigurationHelper

DIRECT_MESSAGE_CHANNEL_NAME = 'Direct Message'

openai_api_key = os.getenv('OPENAI_API_KEY')
bot_token = os.getenv('DISCORD_BOT_TOKEN')

# Initialize 
storage = Storage()
openai_helper = OpenAIHelper()
config_helper = ConfigurationHelper(storage)

intents = discord.Intents.default()
intents.members = True
intents.messages = True  # Enable message intent
intents.message_content = True  # Enable message content intent


class MyBot(commands.Bot):
    async def setup_hook(self):
        print(f'--- setup hook ---')
        # Setup tasks here
        await setup()


bot = MyBot(command_prefix='!', intents=intents)


# Create an instance of the bot
# bot = commands.Bot(command_prefix='!', intents=intents)


# Define an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_message(message):
    start_message=message.content.replace("\n", "\\n")[:32]
    print(f"on_message: ({start_message}...)")

    if isinstance(message.channel, discord.TextChannel) and message.channel.is_nsfw():
        print(f"NSFW channel, skipping message.")
        return

    # Ignore messages sent by the bot
    if message.author == bot.user:
        return

    # Don't process messages sent by the bot itself
    if message.author == bot.user:
        return

    # Process commands first
    ctx = await bot.get_context(message)
    if ctx.valid:
        # It's a command, so skip saving and process the command
        await bot.invoke(ctx)
        return

    is_direct_message = isinstance(message.channel, discord.DMChannel)
    guild_id = message.guild.id if message.guild else None

    channel_name = DIRECT_MESSAGE_CHANNEL_NAME if is_direct_message else message.channel.name

    is_channel_listener=config_helper.is_channel_listened(guild_id, channel_name)
    if not is_direct_message and is_channel_listener:
        str_message_author_id=str(message.author.id)
        str_message_channel_id=str(message.channel.id)
        str_guild_id=str(guild_id)
        storage.insert_message(str_message_author_id, message.content, str_message_channel_id, channel_name, str_guild_id, is_direct_message)

    await bot.process_commands(message)


@bot.event
async def on_message_edit(before, after):
    start_message=after.content.replace("\n", "\\n")[:32]
    print(f"on_message: ({start_message}...)")

    if isinstance(after.channel, discord.TextChannel) and after.channel.is_nsfw():
        print(f"NSFW channel, skipping message.")
        return

    # Ignore messages sent by the bot
    if before.author == bot.user:
        return

    # Ignore messages sent by the bot
    if after.author == bot.user:
        return

    if before.content != after.content:
        guild_id = after.guild.id if after.guild else None
        is_direct_message = isinstance(after.channel, discord.DMChannel)

        channel_name = DIRECT_MESSAGE_CHANNEL_NAME if is_direct_message else after.channel.name

        if not is_direct_message and config_helper.is_channel_listened(guild_id, channel_name):
            storage.update_message(before.id, after.content, str(after.channel.id), after.channel.name, str(guild_id),
                                   is_direct_message)

        print(f"Message edited by {after.author.id}: [Before]: {before.content} [After]: {after.content}")


@bot.event
async def on_close():
    print(f"Closing bot ...", flush=True)
    storage.close()


@bot.command()
@commands.is_owner()  # Only allow the bot owner to use this command
async def mr_authorize_user(ctx, username: str):
    # Find the user by username within the guild
    member = discord.utils.find(lambda m: m.name == username, ctx.guild.members)
    if member is None:
        print(f"Authorize user not found: {username}")
        await ctx.send(f"User {username} not found.")
        return

    # Add the user's ID to storage
    print(f"Authorize user: {member} with ID {member.id}")
    storage.add_authorized_user(member.id)

    await ctx.send(f"User {username} (ID: {member.id}) has been authorized.")


@bot.command()
@commands.has_permissions(administrator=True)
async def mr_add_channel(ctx, channel_name):
    guild_id = str(ctx.guild.id)
    storage.add_listened_channel(guild_id, channel_name)
    await ctx.send(f"Channel {channel_name} has been added to the listened channels for this guild.")


@bot.command()
@commands.has_permissions(administrator=True)
async def mr_del_channel(ctx, channel_name):
    guild_id = str(ctx.guild.id)
    storage.remove_listened_channel(guild_id, channel_name)
    await ctx.send(f"Channel {channel_name} has been added to the listened channels for this guild.")


@bot.command()
@commands.has_permissions(administrator=True)
async def mr_show_config(ctx):
    guild_id = str(ctx.guild.id)
    print(f"show_config...")
    config = storage.getconfig(guild_id)
    print(f"config for {guild_id}: {config}")
    await ctx.send(f"Config: {config}")


@bot.command()
async def ask(ctx, *, question):
    # Ignore messages sent by the bot
    if ctx.author == bot.user:
        return

    if not storage.is_user_authorized(ctx.author.id):
        await ctx.send("You are not authorized to use this command.")
        print(f'not authorized: {ctx.author.id}')
        return
    async with ctx.typing():
        response_txt = await openai_helper.ask_openai(question)
    await ctx.send(response_txt)


@bot.event
async def on_error(event, *args, **kwargs):
    print(f'error.event: {event}')
    print(f'error.args: {args}')
    with open('err.log', 'a', encoding='utf-8') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


async def setup():
    bot.loop.create_task(background_task())


async def background_task():
    scheduler_period = int(os.getenv('SCHEDULER_PERIOD', 1))
    summary_manager = SummaryManager(bot, storage)
    while not bot.is_closed():
        print("Executing scheduled task", flush=True)

        await summary_manager.process_summaries()

        await asyncio.sleep(scheduler_period * 60)


# Run the bot with your token
print(f"token: ...{bot_token[8:-8]}...")
bot.run(bot_token)
