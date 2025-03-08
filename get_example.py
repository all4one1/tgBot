import sqlite3
from pathlib import Path

import sql
import tools
from sql import update
import telebot

example_db_name = "example.db"

def create_example_books():
    con = sqlite3.connect(example_db_name)
    cur = con.cursor()
    # cur.execute("CREATE TABLE if not exists user ("
    cur.execute("CREATE TABLE IF NOT EXISTS example ("
                "id INTEGER,"
                "title	TEXT UNIQUE,"
                "text	BLOB,"
                "PRIMARY KEY(id))")

def decode(bytes):
    import chardet
    try:
        info = chardet.detect(bytes)
        code = info['encoding']
        string = bytes.decode(code)
    except:
        string = "bad encoding"
        code = None
    return string, code



def get_example_list():
    pathlist = Path("examples").glob('*.txt')
    elist = []
    for path in pathlist:
        path_in_str = str(path)
        # elist.append(Path(path_in_str).stem)
        elist.append(path_in_str)
    return elist


def readbytes(path):
    f = open(path, "rb")
    if f.readable() == True:
        bytes = f.read()
        return bytes


def save_all_txt_files_to_database():
    elist = get_example_list()
    for path in elist:
        f = open(path, "rb")
        if f.readable() == True:
            con = sqlite3.connect(example_db_name)
            cur = con.cursor()
            query = "INSERT OR IGNORE INTO example (title, text) VALUES(?, ?)"
            b = readbytes(path)
            title = Path(path).stem
            cur.execute(query, [title, b])
            con.commit()
            cur.close()


def readtitles():
    con = sqlite3.connect(example_db_name)
    cur = con.cursor()
    res = cur.execute(f"SELECT id, title FROM example")
    data = res.fetchall()
    ls = []
    for x in data:
        ls.append(x[1])
    return ls


def transform_blob_to_text(file_number):
    con = sqlite3.connect(example_db_name)
    cur = con.cursor()
    res = cur.execute(f"SELECT text FROM example WHERE id = {file_number}")
    data = res.fetchone()
    text = decode(data[0])
    return text


# database table id is from 1
def save_example_as_current(file_number, user_id):
    text, code = transform_blob_to_text(file_number)
    path = tools.get_current_path(user_id)
    file = open(path, "w", encoding=code)
    file.write(text)
    file.close()
    update(id=user_id, field='isOpen', value=1)
    update(id=user_id, field='position', value=0)


def set_example_book(mes: telebot.types.Message, bot: telebot.TeleBot):
    user = mes.from_user
    id = user.id

    isNew = not (id in tools.userlist)
    if isNew == True:
        lang = user.language_code
        text = {True: "Ошибка, введите /start", False: "Error, you have not /start'ed"}[lang == 'ru']
        bot.send_message(id, text)
        return

    lang = sql.get_lang(id)
    file_id = {True: 1, False: 2}[lang == 'ru']
    save_example_as_current(file_id, id)
    ru = 'Пример установлен: "Чума" - Альбер Камю'
    en = 'The example book is set: "Strange Case of Dr Jekyll and Mr Hyde" - Robert Louis Stevenson'

    bot.send_message(id, {True: ru, False: en}[lang == 'ru'])




#create_example_books()
#save_all_txt_files_to_database()
