import json
import sqlite3
import psycopg
from datetime import datetime


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS file (id text PRIMARY KEY, file_name text, file_path text, file_size integer, chunks text, type text, uploaded text)"
        )
        self.conn.commit()

    def fetch(self):
        self.cur.execute("SELECT * FROM file")
        rows = self.cur.fetchall()
        return rows

    def insert(self, id, file_name, file_path, file_size, chunks, type):
        chunks_str = json.dumps(chunks)
        today = datetime.now()
        self.cur.execute(
            "INSERT INTO file VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id, file_name, file_path, file_size, chunks_str, type, today),
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
            "SELECT * FROM file WHERE file_name=? OR file_path=? OR id=? or file_name LIKE ? or file_path LIKE ? or id LIKE ? or type=?",
            (file_query, file_query, file_query, f"%{file_query}%", f"%{file_query}%", f"%{file_query}%", file_query),
        )
        rows = self.cur.fetchall()
        return rows


class Database2:
    def __init__(self, conn_string):
        self.conn = psycopg.connect(conn_string)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS file (id text PRIMARY KEY, file_name text, file_path text, file_size integer, chunks text, type text, uploaded timestamp)"
        )
        self.conn.commit()

    def fetch(self):
        self.cur.execute("SELECT * FROM file")
        rows = self.cur.fetchall()
        return rows

    def insert(self, id, file_name, file_path, file_size, chunks, type):
        chunks_str = json.dumps(chunks)
        today = datetime.now()
        self.cur.execute(
            "INSERT INTO file VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (id, file_name, file_path, file_size, chunks_str, type, today),
        )
        self.conn.commit()

    def remove(self, id):
        self.cur.execute("DELETE FROM file WHERE id=%s", (id,))
        self.conn.commit()

    def get_file(self, id):
        self.cur.execute("SELECT * FROM file WHERE id=%s", (id,))
        rows = self.cur.fetchall()
        return rows

    def find_file_by_name_or_path_or_id(self, file_query):
        self.cur.execute(
            "SELECT * FROM file WHERE file_name=%s OR file_path=%s OR id=%s or file_name LIKE %s or file_path LIKE %s or id LIKE %s or type=%s",
            (file_query, file_query, file_query, f"%{file_query}%", f"%{file_query}%", f"%{file_query}%", file_query),
        )
        rows = self.cur.fetchall()
        return rows


class DynamicDatabase:
    def __init__(self, db_type, db1=None, db2=None):
        self.db_type = db_type
        self.db1 = db1
        self.db2 = db2

    def fetch(self):
        if self.db_type == 1:
            return self.db1.fetch()
        elif self.db_type == 2:
            return self.db2.fetch()
        elif self.db_type == 3:
            return self.db1.fetch()  # , self.db2.fetch()

    def insert(self, id, file_name, file_path, file_size, chunks, type):
        if self.db_type == 1:
            self.db1.insert(id, file_name, file_path, file_size, chunks, type)
        elif self.db_type == 2:
            self.db2.insert(id, file_name, file_path, file_size, chunks, type)
        elif self.db_type == 3:
            self.db1.insert(id, file_name, file_path, file_size, chunks, type)
            self.db2.insert(id, file_name, file_path, file_size, chunks, type)

    def remove(self, id):
        if self.db_type == 1:
            self.db1.remove(id)
        elif self.db_type == 2:
            self.db2.remove(id)
        elif self.db_type == 3:
            self.db1.remove(id)
            self.db2.remove(id)

    def get_file(self, id):
        if self.db_type == 1:
            return self.db1.get_file(id)
        elif self.db_type == 2:
            return self.db2.get_file(id)
        elif self.db_type == 3:
            return self.db1.get_file(id)  # , self.db2.get_file(id)

    def find_file_by_name_or_path_or_id(self, file_query):
        if self.db_type == 1:
            return self.db1.find_file_by_name_or_path_or_id(file_query)
        elif self.db_type == 2:
            return self.db2.find_file_by_name_or_path_or_id(file_query)
        elif self.db_type == 3:
            return self.db1.find_file_by_name_or_path_or_id(file_query)  # , self.db2.find_file_by_name_or_path_or_id(file_query)
