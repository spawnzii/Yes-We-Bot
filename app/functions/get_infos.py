import requests
from datetime import date
import json
import mysql.connector
import hashlib
import yaml

with open("config/config.yml", 'r') as stream:
    try:
        db_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

user = db_config['mysql']['user']
password = db_config['mysql']['password']
host = db_config['mysql']['host']
database = db_config['mysql']['database']

db_parameters = {
    'user': user,
    'password': password,
    'host': host,
    'database': database
}


def get_user_feed(username):
    r = requests.get(
        f"https://api.yeswehack.com/hacktivity/{username}?page=1&resultsPerPage=500")
    feed = json.loads(r.text)["items"]
    return feed


def checksum_feed(feed):
    feed = str(feed)
    hashed_feed = hashlib.sha256(feed.encode('utf-8')).hexdigest()
    return hashed_feed


def get_user_db():
    conn = mysql.connector.connect(**db_parameters)
    cursor = conn.cursor()
    users = []
    cursor.execute("SELECT name FROM hunters")
    allusers = cursor.fetchall()
    for x in allusers:
        users.extend(x)
    cursor.close()
    conn.close()
    return users


def db_insert_hunter(username, feed):
    conn = mysql.connector.connect(**db_parameters)
    cursor = conn.cursor()
    username = str(username)
    feed = str(feed)
    sql = "INSERT INTO hunters (name,hash) VALUES (%s, %s)"
    val = (username, feed)
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()


def db_update_hash(username, feed):
    conn = mysql.connector.connect(**db_parameters)
    cursor = conn.cursor()
    feed = str(feed)
    username = str(username)
    sql = "UPDATE hunters SET hash=%s WHERE name=%s"
    val = (feed, username)
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()


def db_get_old_hash(username):
    conn = mysql.connector.connect(**db_parameters)
    cursor = conn.cursor()
    cursor.execute(f"SELECT hash FROM hunters WHERE name='{username}'")
    old_feed = cursor.fetchone()
    old_feed = old_feed[0]
    cursor.close()
    conn.close()
    return old_feed


def get_pp_user(username):
    r = requests.get(f'https://api.yeswehack.com/hunters/{username}')
    infos = json.loads(r.text)
    pp = infos["avatar"]["url"]
    return pp


def get_user_infos(username):
    r = requests.get(f'https://api.yeswehack.com/hunters/{username}')
    infos = json.loads(r.text)
    if r.status_code != 404:
        return infos
    else:
        return False


def add_user_to_db(username):
    conn = mysql.connector.connect(**db_parameters)
    cursor = conn.cursor()
    fake_hash = "feedhash"
    if username not in get_user_db():
        r = requests.get(f'https://api.yeswehack.com/hunters/{username}')
        if r.status_code != 404:
            sql = "INSERT INTO hunters(name,hash) VALUES (%s, %s)"
            val = (username, fake_hash)
            cursor.execute(sql, val)
            conn.commit()
            return "User add"
        else:
            return "User not found"

    else:
        return "User already on the db"
    cursor.close()
    conn.close()
