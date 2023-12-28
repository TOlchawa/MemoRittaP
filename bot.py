import discord
import os
import json
from discord.ext import commands
from openai import AsyncOpenAI
from storage import Storage

openai_api_key = os.getenv('OPENAI_API_KEY')
bot_token = os.getenv('DISCORD_BOT_TOKEN')

# Initialize Storage
storage = Storage()


client_openai = AsyncOpenAI(
    api_key=openai_api_key,  # this is also the default, it can be omitted
    organization='org-n9AnfI7a4lvpGr50hbypFLxB',
)


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
    storage.insert_message(str(message.author.id), message.content, str(message.channel.id), message.channel.name, str(guild_id))
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        guild_id = after.guild.id if after.guild else None
        storage.update_message(before.id, after.content, str(after.channel.id), after.channel.name, str(guild_id))
        print(f"Message edited by {after.author.id}: [Before]: {before.content} [After]: {after.content}")



# Define a command
@bot.command()
async def hello(ctx):
    await ctx.send('Hello World!')
    

@bot.event
async def on_close():
    client.close()

@bot.command()
async def add(ctx, key, value):
    # Insert a document into the collection
    storage.insert_document({key: value})
    await ctx.send(f'Added {key}: {value}')



@bot.command()
async def ask(ctx, *, question):
    print(f'question is: {question}')
    try:

        
        completion = await client_openai.chat.completions.create(
            model="gpt-4-1106-preview",
            #response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to help in prepare summary from conversation."},
                {"role": "user", "content": question}
            ],
            max_tokens=100
        )
        
        response_str = completion.model_dump_json(indent=2)
        response_json = json.loads(response_str)
        response_txt = response_json['choices'][0]['message']['content']
        
        print(f'question: {question}; answer: {response_txt}')
        await ctx.send(response_txt)
    except Exception as e:
        await ctx.send('An error occurred: {}'.format(str(e)))


    
@bot.event
async def on_error(event, *args, **kwargs):
    print(f'error: {event}')
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

# Run the bot with your token
bot.run(bot_token)
