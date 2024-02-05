import mysql.connector
import requests
class Database():
    def __init__(self, host, user, password, database) -> None:
        self.db_parameters = {
            'user': user,
            'password': password,
            'host': host,
            'database': database
        }

    def start(self):
        db_state = False
        while db_state == False:
            try:
                self.conn = mysql.connector.connect(**self.db_parameters)
                db_state = True
            except Exception as e:
                print(e)
                db_state = False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS hunters (name VARCHAR(255), hash VARCHAR(255))")
            cursor.close()
            self.conn.close()
        except Exception as e:
            print(e)
            return False
        return True

    def get_users_list(self) -> list:
        conn = mysql.connector.connect(**self.db_parameters)
        cursor = conn.cursor()
        users = []
        cursor.execute("SELECT name FROM hunters")
        allusers = cursor.fetchall()
        for x in allusers:
            users.extend(x)
        cursor.close()
        return users

    def get_old_hash(self, username) -> str:
        conn = mysql.connector.connect(**self.db_parameters)
        cursor = conn.cursor(buffered=True)
        cursor.execute(f"SELECT hash FROM hunters WHERE name='{username}'")
        old_feed = cursor.fetchone()
        old_feed = old_feed[0]
        cursor.close()
        conn.close()
        return old_feed

    def update_hash(self, username, feed) -> None:
        conn = mysql.connector.connect(**self.db_parameters)
        cursor = conn.cursor()
        feed = str(feed)
        username = str(username)
        sql = "UPDATE hunters SET hash=%s WHERE name=%s"
        val = (feed, username)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        conn.close()

    def add_user(self, username) -> int:
        conn = mysql.connector.connect(**self.db_parameters)
        cursor = conn.cursor()
        fake_hash = "feedhash"
        if username not in self.get_users_list():
            r = requests.get(f'https://api.yeswehack.com/hunters/{username}')
            if r.status_code != 404:
                sql = "INSERT INTO hunters(name,hash) VALUES (%s, %s)"
                val = (username, fake_hash)
                cursor.execute(sql, val)
                conn.commit()
                cursor.close()
                conn.close()
                return 0
            else:
                return 2
        else:
            return 1
