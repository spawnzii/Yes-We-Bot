from functions.get_infos import *
from functions.messages import *
import discord
from discord.ext import commands
from discord.ext import tasks
import mysql.connector
from datetime import date
import secrets
import time
import asyncio
import concurrent.futures

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!",description="Yes We Hack",intents=intents)

@tasks.loop(minutes=1,reconnect=True)
async def check_feed():
    start_time = time.time()
    embed = send_bugs()
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Temps d'exécution : {execution_time} secondes")

    if embed != False:
        discord_server = bot.get_channel() # Your channel id
        for e in embed:
            await discord_server.send(embed=e)
    else:
        pass

@bot.event
async def on_ready():
    print("Bot is Ready")
    check_feed.start()

@bot.command()
async def infos(ctx,user):
    await ctx.send(embed=send_infos(user))

@bot.command()
async def add(ctx,user):
    await ctx.send(send_add_user(user))


bot.run("") # Your token
