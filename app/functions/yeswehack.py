import requests
import hashlib


class YesWeHack:
    def __init__(self) -> None:
        pass

    def get_user_feed(self, username):
        r = requests.get(
            f"https://api.yeswehack.com/hacktivity/{username}?page=1&resultsPerPage=500")

        try:
            feed = r.json()["items"]
        except:
            feed = None
        return feed

    def get_pp_user(self, username):
        r = requests.get(f'https://api.yeswehack.com/hunters/{username}')
        infos = r.json()
        try:
            pp = infos["avatar"]["url"]
        except:
            pp = "https://cdn-yeswehack.com/business-unit/logo/699717c7ac0d05bbccf13972496abc02"
        return pp

    def get_user_infos(self, username):
        r = requests.get(f'https://api.yeswehack.com/hunters/{username}')
        infos = r.json()
        if r.status_code != 404:
            return infos
        else:
            return False

    def checksum_feed(self, feed):
        feed = str(feed)
        hashed_feed = hashlib.sha256(feed.encode('utf-8')).hexdigest()
        return hashed_feed
