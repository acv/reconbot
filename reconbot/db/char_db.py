import sqlite3
import os.path


class Char(object):
    def __init__(self, char_db, char_id, username, refresh_token, orig_refresh_token):
        self.char_db = char_db
        self.char_id = char_id
        self.username = username
        self.refresh_token = refresh_token
        self.orig_refresh_token = orig_refresh_token

    def save(self):
        c = self.char_db.dbh.cursor()
        c.execute("""INSERT OR REPLACE INTO chars (char_id, username, refresh_token, orig_refresh_token)
                     VALUES (?, ?, ?, ?)""", (self.char_id, self.username, self.refresh_token,
                                              self.orig_refresh_token))
        self.char_db.dbh.commit()
        c.close()


class CharDB(object):
    def __init__(self, config):
        """

        Parameters
        ----------
        config: ...Config
        """
        self.db_file_name = os.path.join(os.path.dirname(config.config_file_name), "reconbot.db")
        self.dbh = sqlite3.connect(self.db_file_name)
        self.dbh.row_factory = sqlite3.Row
        self.init_db()
        self.chars = self.load_chars(config)

    def init_db(self):
        c = self.dbh.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS chars (char_id TEXT, username TEXT, refresh_token TEXT,
                     orig_refresh_token TEXT)""")
        c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS char_pkey ON chars (char_id)""")
        c.close()

    def load_chars(self, config):
        chars = []

        for c in config.esi_config['characters']:
            chars.append(self.get_char(c['char_id'], c['username'], c['refresh_token']))

        return chars

    def get_char(self, char_id, username, refresh_token):
        c = self.dbh.cursor()
        c.execute("""SELECT char_id, username, refresh_token, orig_refresh_token
                     FROM chars WHERE char_id = ?""", (char_id,))
        row = c.fetchone()
        if row is None:
            char = Char(self, char_id, username, refresh_token, refresh_token)
            char.save()
        else:
            char = Char(self, row['char_id'], row['username'], row['refresh_token'],
                        row['orig_refresh_token'])
            if row['orig_refresh_token'] != refresh_token:  # Config file newer!
                char.refresh_token = refresh_token
                char.orig_refresh_token = refresh_token
                char.save()
        return char
