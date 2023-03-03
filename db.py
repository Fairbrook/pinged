import sqlite3


class DB:

    def __init__(self, db_name: str) -> None:
        self.connection = sqlite3.connect(db_name)
        self.cursor = None

    def get_cursor(self) -> sqlite3.Cursor:
        if(self.cursor is None):
            self.cursor = self.get_connection().cursor()
        return self.cursor

    def get_connection(self) -> sqlite3.Connection:
        if (self.connection is None):
            raise Exception("No db connection")
        return self.connection

    def migrate(self):
        self.get_cursor().execute(
            "CREATE TABLE IF NOT EXISTS domains(url TEXT, status NUMERIC, last_elapsed NUMBER, PRIMARY KEY(url))")

    def save_url(self, url: str):
        self.get_cursor().execute("INSERT INTO domains(url) VALUES(?)", (url, ))
        self.get_connection().commit()

    def update_latest(self, url: str, status: bool, elapsed: float):
        self.get_cursor().execute(
            "UPDATE domains SET status=?, last_elapsed=? WHERE url=?", (status, elapsed, url))
        self.get_connection().commit()

    def rm(self, url: str):
        self.get_cursor().execute("DELETE FROM domains WHERE url =?", (url,))
        self.get_connection().commit()

    def get_all(self):
        list = self.get_cursor().execute("SELECT * FROM domains").fetchall()
        return [{'url': item[0], 'status':item[1], 'elapsed':item[2]}for item in list]
