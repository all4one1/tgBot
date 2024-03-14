import sqlite3

db_name = "userbase.db"


def create_db():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    # cur.execute("CREATE TABLE if not exists user ("
    cur.execute("CREATE TABLE user ("
                "id INTEGER,"
                "isOpen	INTEGER DEFAULT 0,"
                "position	INTEGER DEFAULT 0,"
                "pagesize	INTEGER DEFAULT 1024,"
                "frequency	INTEGER DEFAULT 0,"
                "language   TEXT DEFAULT ru,"
                "lastcall   INTEGER DEFAULT 0,"
                "PRIMARY KEY(id))")


def get_data(id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = ("SELECT "
             "isOpen, position, pagesize, frequency "
             "FROM user "
             "WHERE id = " + str(id))
    res = cur.execute(query)
    return res.fetchone()


# TODO: check why return turple is ok here (without [0])
def get_lang(id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = ("SELECT "
             "language "
             "FROM user "
             "WHERE id = " + str(id))
    res = cur.execute(query)
    return res.fetchone()


# TODO: update and change at once?
def get_last(id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = ("SELECT "
             "lastcall "
             "FROM user "
             "WHERE id = " + str(id))
    res = cur.execute(query)
    return res.fetchone()[0]

def get_user_id_list():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    res = cur.execute("SELECT id FROM user")

    ls = []
    for x in list(res):
        ls.append(x[0])
    return ls


def show_db():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM user")
    ls = list(res)
    s = ""
    for x in ls:
        s += ''.join(str(x)) + "\n"
    return s


def add_new_user(id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO user (id) VALUES(" + str(id) + ")")
    con.commit()


def update(id, field, value):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("UPDATE user SET " + field + " = " + str(value) + " WHERE id = " + str(id))
    con.commit()


def update_text(id, field, value):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    value_with_quotes = f"'{str(value)}'"
    cur.execute("UPDATE user SET " + field + " = " + value_with_quotes + " WHERE id = " + str(id))
    con.commit()


def create_example_books():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    # cur.execute("CREATE TABLE if not exists user ("
    cur.execute("CREATE TABLE example ("
                "id INTEGER,"
                "author	TEXT,"
                "title	TEXT,"
                "text	TEXT,"
                "PRIMARY KEY(id))")


con = sqlite3.connect(db_name)
cur = con.cursor()
value = ""
with open('example.txt', 'r') as file:
    value = file.read()
value_with_quotes = f"'{str(value)}'"
cur.execute("UPDATE example SET text = " + value_with_quotes + " WHERE id = 1")
con.commit()

# import os
# os._exit(0)

# data = [(123, 1982, 1000), (1488, 1983, 1000), (209, 1979, 3000),]
# cur.executemany("INSERT OR IGNORE INTO user VALUES(?, ?, ?)", data)
# con.commit()
# cur.execute("UPDATE user SET lastpos = -1 WHERE id = 12345")
# con.commit()
