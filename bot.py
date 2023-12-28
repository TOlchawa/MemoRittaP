import discord
import os
import json
from discord.ext import commands
from storage import Storage
from openai_helper import OpenAIHelper

DIRECT_MESSAGE_CHANNEL_NAME = 'Direct Message'

openai_api_key = os.getenv('OPENAI_API_KEY')
bot_token = os.getenv('DISCORD_BOT_TOKEN')

# Initialize 
storage = Storage()
openai_helper = OpenAIHelper()


intents = discord.Intents.default()
intents.messages = True  # Enable message intent
intents.message_content = True  # Enable message content intent


# Create an instance of the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Define an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    guild_id = message.guild.id if message.guild else None
    is_direct_message = isinstance(message.channel, discord.DMChannel)
    
    channel_name = DIRECT_MESSAGE_CHANNEL_NAME if is_direct_message else message.channel.name

    storage.insert_message(str(message.author.id), message.content, str(message.channel.id), channel_name, str(guild_id), is_direct_message)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        guild_id = after.guild.id if after.guild else None
        is_direct_message = isinstance(after.channel, discord.DMChannel)

        channel_name = DIRECT_MESSAGE_CHANNEL_NAME if is_direct_message else after.channel.name

        storage.update_message(before.id, after.content, str(after.channel.id), after.channel.name, str(guild_id), is_direct_message)
        print(f"Message edited by {after.author.id}: [Before]: {before.content} [After]: {after.content}")


# Define a command
@bot.command()
async def hello(ctx):
    await ctx.send('Hello World!')
    

@bot.event
async def on_close():
    client.close()


@bot.command()
async def ask(ctx, *, question):
    async with ctx.typing():
        response_txt = await openai_helper.ask_openai(question)
    await ctx.send(response_txt)


@bot.event
async def on_error(event, *args, **kwargs):
    print(f'error: {event}')
    with open('err.log', 'a', encoding='utf-8') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


# Run the bot with your token
bot.run(bot_token)
