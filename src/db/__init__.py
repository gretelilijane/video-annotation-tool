import sqlite3


class Database:
    conn = None
    cur = None


def connect(uri):
    Database.conn = sqlite3.connect(uri)
    Database.cur = Database.conn.cursor()

def execute(query, params=tuple()):
    Database.cur.execute(query, params)

def executemany(query, seq_of_params):
    Database.cur.executemany(query, seq_of_params)

def commit():
    Database.conn.commit()

def fetchone():
    return Database.cur.fetchone()

def fetchall():
    return Database.cur.fetchall()

def lastrowid():
    return Database.cur.lastrowid

def close():
    Database.conn.close()
