from functions.database import Database
from functions.messages import *
from functions.config import Config
import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import date
import time

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!",
                   description="Yes We Hack", intents=intents)

# Load the configuration
config = Config('config/config.yml')
config.load()

# Get discord, and database details from the config
discord_token = config.get_config('discord', 'token')
discord_channel = config.get_config('discord', 'channel')
discord_admins = config.get_config('discord', 'admins')
db_host = config.get_config('mysql', 'host')
db_user = config.get_config('mysql', 'user')
db_password = config.get_config('mysql', 'password')
db_database = config.get_config('mysql', 'database')


async def send_embed(embed):
    channel = bot.get_channel(discord_channel)
    if isinstance(embed, list):
        for x in embed:
            await channel.send(embed=x)
    elif isinstance(embed, discord.Embed):
        await channel.send(embed=embed)
    else:
        print("Nothing to send")


@tasks.loop(minutes=1, reconnect=True)
async def check_feed(db: Database):
    start_time = time.time()
    embed = send_bugs(db)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Temps d'exécution : {execution_time} secondes")
    await send_embed(embed)


@bot.event
async def on_ready():
    print("Bot is Ready")
    print("Initializing database")
    db = Database(db_host, db_user, db_password, db_database)
    if db.start():
        print("Database initialized")
    else:
        print("Database initialization failed")
        exit(1)

    check_feed.start(db)


@bot.command()
async def infos(ctx, user):
    db = Database(db_host, db_user, db_password, db_database)
    user = user.lower()
    embed = user_infos(user)
    await ctx.send(embed=embed)

@bot.command()
async def add(ctx, user):
    db = Database(db_host, db_user, db_password, db_database)
    if ctx.author.id in discord_admins:
        user = user.lower()
        embed = add_user(db, user)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(
            name="Error", value=f"You are not allowed to use this command")
        await ctx.send(embed=embed)

print("Starting bot")
bot.run(discord_token)
