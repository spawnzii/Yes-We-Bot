from functions.get_infos import *
import discord
from discord.ext import commands
from discord.ext import tasks
import mysql.connector
from datetime import date
import secrets


bot = commands.Bot(command_prefix="!",description="Yes We Hack")

@tasks.loop(minutes=1)
async def check_feed():
    icons_bug = ["🐞","🪰","🪲","🪳","🕷","🐜"]
    hunters = ["laluka","spawnzii","w0rty","perce","sicarius","geluchat","itarow","w00dy","yo0x-1","mizu"]
    for hunter in hunters:
        new = checksum_feed(get_user_feed(hunter))
        old = db_get_old_hash(hunter)
        feed = get_user_feed(hunter)
        bug = feed[0]["report"]["bug_type"]["name"]
        pseudo = feed[0]["report"]["hunter"]["username"]
        status = feed[0]["status"]["workflow_state"]
        pp = get_pp_user(hunter)
        
        if new != old and status == "new":
            today = date.today()
            icons = secrets.choice(icons_bug)
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(
            name=f"{hunter} has found a new bug {icons}", url=pp, icon_url=pp)
            embed.add_field(name="**Bug Type**", value=bug, inline=True)
            embed.add_field(name="**Status**", value=status, inline=True)
            embed.add_field(name="**Date**", value=today, inline=False)
            discord_server = bot.get_channel(831949020804939837)       # Your channel id
            await discord_server.send(embed=embed)
            db_update_hash(hunter, new)
        
        if new != old and status == "accepted":
            today = date.today()
            icons = secrets.choice(icons_bug)
            embed = discord.Embed(color=discord.Color.green())
            embed.set_author(
            name=f"Congrats ! {hunter}'s report was {status} 🔥", url=pp, icon_url=pp)
            embed.add_field(name="**Bug Type** :", value=bug, inline=True)
            embed.add_field(name="**Date ** :", value=today, inline=True)
            discord_server = bot.get_channel(831949020804939837)       # Your channel id
            await discord_server.send(embed=embed)
            db_update_hash(hunter, new)
        
        if new != old and status == "resolved":
            today = date.today()
            icons = secrets.choice(icons_bug)
            today = date.today()
            embed = discord.Embed(color=discord.Color.dark_grey())
            embed.set_author(
            name=f"No more bugs! {hunter}'s report was {status} 🦾", url=pp, icon_url=pp)
            embed.add_field(name="** Bug Type ** :", value=bug, inline=True)
            embed.add_field(name="** Date ** :", value=today, inline=True)
            discord_server = bot.get_channel(831949020804939837)       # Your channel id
            await discord_server.send(embed=embed)
            db_update_hash(hunter, new)


@bot.event
async def on_ready():
    print("Bot is Ready")
    check_feed.start()

@bot.command()
async def infos(ctx,user):
    if get_user_infos(user) is False:
        await ctx.send(f"User **{user}** not found or his profile is private")
    else:
        feed = get_user_feed(user.lower())
        bug = feed[0]["report"]["bug_type"]["name"]
        infos = get_user_infos(user.lower())
        rank = infos["rank"]
        point = infos["points"]
        report = infos["nb_reports"]
        impact = infos["impact"]
        pp = infos["avatar"]["url"]

        if impact == "kyc_status":
            impact = "None"

        if "default_image" in pp:
            pp = "https://cdn-yeswehack.com/business-unit/logo/699717c7ac0d05bbccf13972496abc02"

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(
        name=f"Profile of {user}", url=pp, icon_url=pp)
        embed.add_field(name="Rank 🏆", value=rank, inline=True)
        embed.add_field(name="Points 🏅", value=point, inline=True)
        embed.add_field(name="Reports 🚩", value=report, inline=True)
        embed.add_field(name="Impact 💀", value=impact, inline=True)
        embed.add_field(name="Last finding 🪲", value=bug, inline=False)
        await ctx.send(embed=embed)
        
bot.run("") # Your token
