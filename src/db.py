import json
import sqlite3


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS file (id text PRIMARY KEY, file_name text, file_path text, file_size integer, chunks text)"
        )
        self.conn.commit()

    def fetch(self):
        self.cur.execute("SELECT * FROM file")
        rows = self.cur.fetchall()
        return rows

    def insert(self, id, file_name, file_path, file_size, chunks):
        chunks_str = json.dumps(chunks)
        self.cur.execute(
            "INSERT INTO file VALUES (?, ?, ?, ?, ?)",
            (id, file_name, file_path, file_size, chunks_str),
        )
        self.conn.commit()

    def remove(self, id):
        self.cur.execute("DELETE FROM file WHERE id=?", (id,))
        self.conn.commit()

    def get_file(self, id):
        self.cur.execute("SELECT * FROM file WHERE id=?", (id,))
        rows = self.cur.fetchall()
        return rows

    def find_file_by_name_or_path_or_id(self, file_query):
        self.cur.execute(
            "SELECT * FROM file WHERE file_name=? OR file_path=? OR id=?",
            (file_query, file_query, file_query),
        )
        rows = self.cur.fetchall()
        return rows
