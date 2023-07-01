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
import yaml

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!",description="Yes We Hack",intents=intents)

with open("config/config.yml", 'r') as stream:
    try:
        discord_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

discord_token = discord_config["discord"]["token"]
discord_channel = discord_config["discord"]["channel"]


@tasks.loop(minutes=1,reconnect=True)
async def check_feed():
    start_time = time.time()
    embed = send_bugs()
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Temps d'exécution : {execution_time} secondes")

    if embed != False:
        discord_server = bot.get_channel(discord_channel)
        for e in embed:
            await discord_server.send(embed=e)
    else:
        pass

@bot.event
async def on_ready():
    print("Bot is Ready")
    time.sleep(10) # Wait for db to be ready
    check_feed.start()

@bot.command()
async def infos(ctx,user):
    await ctx.send(embed=send_infos(user.lower()))

@bot.command()
async def add(ctx,user):
    if ctx.author.id in discord_config["discord"]["admins"]:
        msg, color = send_add_user(user.lower())
        embed = discord.Embed(title="Add User", color=color)
        embed.add_field(name="Status", value=msg, inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, you don't have the permission to use this command")

bot.run(discord_token)