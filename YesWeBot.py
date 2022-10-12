#!/usr/bin/python3

import hashlib
from asyncio import tasks
import discord
from discord.ext import commands
from discord.ext import tasks
import requests
from datetime import date
import secrets
import os

bot = commands.Bot(command_prefix="!",description="Yes We Hack")

def get_last_feed():
    url = "https://api.yeswehack.com/hacktivity"
    r = requests.get(url)
    feed = r.text
    return feed

def get_hashed_feed(feed):
    hashed_feed = hashlib.sha256(feed.encode('utf-8')).hexdigest()
    return hashed_feed

def user_infos(user):
    url = f"https://api.yeswehack.com/hunters/{user}"
    r = requests.get(url)
    if r.status_code != 404:
        return r.text
    else:
        return False

os.environ["YWHash"] = "empty"

@tasks.loop(minutes=1)
async def check_feed():
    last_feed = get_last_feed()

    if os.environ['YWHash'] != get_hashed_feed(last_feed):
        os.environ['YWHash'] = get_hashed_feed(last_feed)
        
        hunters = ["spawnzii","w0rty","perce","sicarius","_yo0x","itarow","w00dy"] # use lowercase usernames
        last_feed = last_feed.rsplit('"')
        bug = last_feed[last_feed.index("bug_type")+4]
        user = last_feed[last_feed.index("username")+2]
        status = last_feed[last_feed.index("status")+4]
        avatar_url = last_feed[last_feed.index("url")+2]
        icons_bug = ["🐞","🪰","🪲","🪳","🕷","🐜"]

        if "default_image" in avatar_url:
            avatar_url = "https://cdn-yeswehack.com/business-unit/logo/699717c7ac0d05bbccf13972496abc02"

        if user.lower() in hunters and status.lower() == "new":
            today = date.today()
            icons = secrets.choice(icons_bug)
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(
            name=f"{user} has found a new bug {icons}", url=avatar_url, icon_url=avatar_url)
            embed.add_field(name="**Bug Type**", value=bug, inline=True)
            embed.add_field(name="**Status**", value=status, inline=True)
            embed.add_field(name="**Date**", value=today, inline=False)
            discord_server = bot.get_channel(831949020804939837)       # Your channel id
            await discord_server.send(embed=embed)

        if user.lower() in hunters and status.lower() == "accepted":
    
            today = date.today()
            embed = discord.Embed(color=discord.Color.green())
            embed.set_author(
            name=f"Congrats ! {user}'s report was {status} 🔥", url=avatar_url, icon_url=avatar_url)
            embed.add_field(name="**Bug Type** :", value=bug, inline=True)
            embed.add_field(name="**Date ** :", value=today, inline=True)
            discord_server = bot.get_channel(831949020804939837)       # Your channel id
            await discord_server.send(embed=embed)

        if user.lower() in hunters and status.lower() == "resolved":

            today = date.today()
            embed = discord.Embed(color=discord.Color.dark_grey())
            embed.set_author(
            name=f"No more bugs! {user}'s report was {status} 🦾", url=avatar_url, icon_url=avatar_url)
            embed.add_field(name="** Bug Type ** :", value=bug, inline=True)
            embed.add_field(name="** Date ** :", value=today, inline=True)
            discord_server = bot.get_channel(831949020804939837)       # Your channel id
            await discord_server.send(embed=embed)


@bot.event
async def on_ready():
    print("Bot is Ready")
    check_feed.start()

@bot.command()
async def infos(ctx,user):
    if user_infos(user) is False:
        await ctx.send(f"User **{user}** not found or his profile is in private")
    else:
        infos = user_infos(user).rsplit('"')
        rank = infos[infos.index('rank') + 1]
        rank = rank.replace(",","").replace(":","")
        point = infos[infos.index('points') + 1]
        point = point.replace(",","").replace(":","")
        report = infos[infos.index('nb_reports') + 1]
        report = report.replace(",","").replace(":","")
        impact = infos[infos.index('impact') + 2]
        avatar_url = infos[infos.index('url') + 2]

        if impact == "kyc_status":
            impact = "None"

        if "default_image" in avatar_url:
            avatar_url = "https://cdn-yeswehack.com/business-unit/logo/699717c7ac0d05bbccf13972496abc02"

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(
        name=f"Profile of {user}", url=avatar_url, icon_url=avatar_url)
        embed.add_field(name="Rank 🏆", value=rank, inline=True)
        embed.add_field(name="Points 🏅", value=point, inline=True)
        embed.add_field(name="Reports 🚩", value=report, inline=True)
        embed.add_field(name="Impact 💀", value=impact, inline=True)
        await ctx.send(embed=embed)


bot.run("") # add your token.
