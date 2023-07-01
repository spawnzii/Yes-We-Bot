import discord
from .get_infos import *
import concurrent.futures
import secrets


def send_infos(user):
    if get_user_infos(user) is False:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(
            name="Error", value=f"User **{user}** not found or his profile is private")
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
    return embed


def send_add_user(user):
    add = add_user_to_db(user)
    if add == "User not found":
        msg = f"User **{user}** not found or his profile is private"
        color = discord.Color.red()
    if add == "User already on the db":
        msg = f"User **{user}** is already in the database."
        color = discord.Color.yellow()
    if add == "User add":
        msg = f"User **{user}** added to the database."
        color = discord.Color.green()

    return msg, color


def send_bugs():
    icons_bug = ["🐞", "🪰", "🪲", "🪳", "🕷", "🐜"]
    hunters = get_user_db()
    futures = []
    arr_embed = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        feed_pp = []
        for hunter in hunters:

            feed_future = executor.submit(get_user_feed, hunter)
            pp = executor.submit(get_pp_user, hunter)
            futures.append(feed_future)
            feed_pp.append(pp)

        feeds = [future.result() for future in futures]
        all_pp = [pp.result() for pp in feed_pp]

        checksum_futures = [executor.submit(
            checksum_feed, feed) for feed in feeds]
        old_hash_futures = [executor.submit(
            db_get_old_hash, hunter) for hunter in hunters]

        checksums = [future.result() for future in checksum_futures]
        old_hashes = [future.result() for future in old_hash_futures]

        for feed, checksum, old_hash, pp in zip(feeds, checksums, old_hashes, all_pp):
            bug = feed[0]["report"]["bug_type"]["name"]
            pseudo = feed[0]["report"]["hunter"]["slug"]
            status = feed[0]["status"]["workflow_state"]

            if checksum != old_hash and status == "new":
                today = date.today()
                icons = secrets.choice(icons_bug)
                embed = discord.Embed(color=discord.Color.red())
                embed.set_author(
                    name=f"{pseudo} has found a new bug {icons}", url=pp, icon_url=pp)
                embed.add_field(name="**Bug Type**", value=bug, inline=True)
                embed.add_field(name="**Status**", value=status, inline=True)
                embed.add_field(name="**Date**", value=today, inline=False)
                db_update_hash(pseudo, checksum)
                arr_embed.append(embed)

            if checksum != old_hash and status == "accepted":
                today = date.today()
                icons = secrets.choice(icons_bug)
                embed = discord.Embed(color=discord.Color.green())
                embed.set_author(
                    name=f"Congrats ! {pseudo}'s report was {status} 🔥", url=pp, icon_url=pp)
                embed.add_field(name="**Bug Type** :", value=bug, inline=True)
                embed.add_field(name="**Date ** :", value=today, inline=True)
                db_update_hash(pseudo, checksum)
                arr_embed.append(embed)

            if checksum != old_hash and status == "resolved":
                today = date.today()
                icons = secrets.choice(icons_bug)
                today = date.today()
                embed = discord.Embed(color=discord.Color.dark_grey())
                embed.set_author(
                    name=f"No more bugs! {pseudo}'s report was {status} 🦾", url=pp, icon_url=pp)
                embed.add_field(name="** Bug Type ** :",
                                value=bug, inline=True)
                embed.add_field(name="** Date ** :", value=today, inline=True)
                db_update_hash(pseudo, checksum)
                arr_embed.append(embed)

            else:
                pass

        if len(arr_embed) > 0:
            return arr_embed
        else:
            return False
