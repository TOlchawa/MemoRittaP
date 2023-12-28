import discord
import os
from discord.ext import commands
from pymongo import MongoClient
from openai import AsyncOpenAI

openai_api_key = os.getenv('OPENAI_API_KEY')
bot_token = os.getenv('DISCORD_BOT_TOKEN')
mongodb_url = os.getenv('MONGODB_URL')


client_openai = AsyncOpenAI(
    api_key=openai_api_key,  # this is also the default, it can be omitted
    organization='org-n9AnfI7a4lvpGr50hbypFLxB',
)


intents = discord.Intents.default()
# Enable any additional intents as needed
# For example, if you need member join events:
# intents.members = True

client = MongoClient('mongodb://localhost:27017/')
db = client.memorittap
collection = db.notes


# Create an instance of the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Define an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

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
    collection.insert_one({key: value})
    await ctx.send(f'Added {key}: {value}')



@bot.command()
async def ask(ctx, *, question):
    print(f'question is: {question}')
    try:

        
        completion = await client_openai.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": "Who won the world series in 2020?"}
            ]
        )
        
        response_json = completion.model_dump_json(indent=2)
        response_txt = response_json.choices[0].content
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
bot.run('MTE4OTkxNDIxMTQ4MTAzMDY4Ng.G_OLEn.HeZZrKeD16e4cZh1DIjoB3H_JMYY9WMkZma86M')
