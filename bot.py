import discord
from discord.ext import commands

# Create an instance of the bot
bot = commands.Bot(command_prefix='!')

# Define an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Define a command
@bot.command()
async def hello(ctx):
    await ctx.send('Hello World!')

# Run the bot with your token
bot.run('MTE4OTkxNDIxMTQ4MTAzMDY4Ng.G_OLEn.HeZZrKeD16e4cZh1DIjoB3H_JMYY9WMkZma86M')
