from discord import Embed, Color
from .yeswehack import *
from .database import *
import concurrent.futures
import secrets
from datetime import date

ywh = YesWeHack()

def user_infos(user):
    user = user.lower()
    if ywh.get_user_infos(user) is False:
        embed = Embed(color=Color.red())
        embed.add_field(
            name="Error", value=f"User **{user}** not found or his profile is private")
    else:
        feed = ywh.get_user_feed(user)
        bug = feed[0]["report"]["bug_type"]["name"]
        infos = ywh.get_user_infos(user)
        rank = infos["rank"]
        point = infos["points"]
        report = infos["nb_reports"]
        impact = infos["impact"]
        pp = infos["avatar"]["url"]

        if impact == "kyc_status":
            impact = "None"

        if "default_image" in pp:
            pp = "https://cdn-yeswehack.com/business-unit/logo/699717c7ac0d05bbccf13972496abc02"

        embed = Embed(color=Color.blue())
        embed.set_author(
            name=f"Profile of {user}", url=pp, icon_url=pp)
        embed.add_field(name="Rank 🏆", value=rank, inline=True)
        embed.add_field(name="Points 🏅", value=point, inline=True)
        embed.add_field(name="Reports 🚩", value=report, inline=True)
        embed.add_field(name="Impact 💀", value=impact, inline=True)
        embed.add_field(name="Last finding 🪲", value=bug, inline=False)
    return embed


def add_user(db, user):
    add_user_state = db.add_user(user)
    match add_user_state:
        case 0:
            msg = f"User **{user}** added to the database."
            color = Color.green()
        case 1:
            msg = f"User **{user}** is already in the database."
            color = Color.yellow()
        case 2:
            msg = f"User **{user}** not found or his profile is private"
            color = Color.red()

        case _:
            msg = "Error"
    embed = Embed(title="Add user", color=color)
    embed.add_field(name="**Status**", value=msg, inline=True)
    return embed


def send_bugs(db: Database):
    icons_bug = ["🐞", "🪰", "🪲", "🪳", "🕷", "🐜"]
    hunters = db.get_users_list()
    if len(hunters) == 0:
        return False
    futures = []
    arr_embed = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        feed_pp = []
        for hunter in hunters:
            feed_future = executor.submit(ywh.get_user_feed, hunter)
            pp = executor.submit(ywh.get_pp_user, hunter)
            futures.append(feed_future)
            feed_pp.append(pp)
        feeds = [future.result() for future in futures]
        all_pp = [pp.result() for pp in feed_pp]

        checksum_futures = [executor.submit(
            ywh.checksum_feed, feed) for feed in feeds]
        old_hash_futures = [executor.submit(
            db.get_old_hash, hunter) for hunter in hunters]

        checksums = [future.result() for future in checksum_futures]
        old_hashes = [future.result() for future in old_hash_futures]

        for feed, checksum, old_hash, pp in zip(feeds, checksums, old_hashes, all_pp):
            try:
                bug = feed[0]["report"]["bug_type"]["name"]
            except IndexError:
                continue
            pseudo = feed[0]["report"]["hunter"]["slug"]
            status = feed[0]["status"]["workflow_state"]

            if checksum != old_hash and status == "new":
                today = date.today()
                icons = secrets.choice(icons_bug)
                embed = Embed(color=Color.red())
                embed.set_author(
                    name=f"{pseudo} has found a new bug {icons}", url=pp, icon_url=pp)
                embed.add_field(name="**Bug Type**", value=bug, inline=True)
                embed.add_field(name="**Status**", value=status, inline=True)
                embed.add_field(name="**Date**", value=today, inline=False)
                db.update_hash(pseudo, checksum)
                arr_embed.append(embed)

            if checksum != old_hash and status == "accepted":
                today = date.today()
                icons = secrets.choice(icons_bug)
                embed = Embed(color=Color.green())
                embed.set_author(
                    name=f"Congrats ! {pseudo}'s report was {status} 🔥", url=pp, icon_url=pp)
                embed.add_field(name="**Bug Type** :", value=bug, inline=True)
                embed.add_field(name="**Date ** :", value=today, inline=True)
                db.update_hash(pseudo, checksum)
                arr_embed.append(embed)

            if checksum != old_hash and status == "resolved":
                today = date.today()
                icons = secrets.choice(icons_bug)
                today = date.today()
                embed = Embed(color=Color.dark_grey())
                embed.set_author(
                    name=f"No more bugs! {pseudo}'s report was {status} 🦾", url=pp, icon_url=pp)
                embed.add_field(name="** Bug Type ** :",
                                value=bug, inline=True)
                embed.add_field(name="** Date ** :", value=today, inline=True)
                db.update_hash(pseudo, checksum)
                arr_embed.append(embed)

            else:
                pass

        if len(arr_embed) > 0:
            return arr_embed
        else:
            return False
