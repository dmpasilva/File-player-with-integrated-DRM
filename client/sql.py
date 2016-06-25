# Client database init
import sqlite3
import config

db = config.database

def init_sql():
    # File TABLE
    c = sqlite3.connect(db).cursor()

    query = "create table books(" \
            "id integer primary key autoincrement, " \
            "local_filename text, " \
            "title text," \
            "owner text)"

    c.execute(query)

def insertRows(table, values, nrows):
    c = sqlite3.connect(db)
    cursor = c.cursor()
    query = "pragma table_info(" + str(table) + ")"
    cursor.execute(query)
    cols = len(cursor.fetchall())

    query = "insert into " + table + " values("
    for i in range(cols):
        if i != cols-1:
            query += "?,"
        else:
            query +="?)"

    if nrows == 1:
        cursor.execute(query, values)
    else:
        cursor.executemany(query, values)

    c.commit()
    cursor.close()
