# TODO: some things in this module are redundant or duplicated
#       (like functions to process a text)


import os
import sys


from src import sql
from datetime import datetime
from math import ceil
import telebot

userlist = []
TOKEN = ""
rootdir = ""


def init():
    res = process_argv()
    if res == 1:
        quit()

    if not os.path.exists("User"):
        os.makedirs("User")
    if not os.path.exists("log.txt"):
        f = open("log.txt", "w")
        f.close()
    if not os.path.exists(sql.db_name):
        sql.create_db()

    global TOKEN, userlist
    TOKEN = get_token()
    userlist = sql.get_user_id_list()


def process_argv():
    args = sys.argv
    if len(args) == 1:
        return 0

    first = args[1]
    if first == "createdatabase":
        if os.path.exists(sql.db_name):
            os.remove(sql.db_name)
        sql.create_db()
        print("database created")
        return 1

    return 0


def log(str):
    now = datetime.now()
    daytime = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("log.txt", "a")
    f.write(daytime + ": " + str + "\n")
    f.close()


def to_int(str):
    i = 0
    try:
        i = int(str)
        if i < 0:
            i = -1
    except:
        i = -1
    return i


def get_current_path(id):
    return os.path.join("User", str(id), "current.txt")


def get_book2(path):
    book = ""
    f = open(path, "r")
    if f.readable() == True:
        book = f.read()
    return book


def get_book(path):
    book = ""
    f = open(path, "rb")
    if f.readable() == True:
        bytes = f.read()
        book = decode(bytes)
    return book


def decode(bytes):
    import chardet
    try:
        info = chardet.detect(bytes)
        type = info['encoding']
        string = bytes.decode(type)
    except:
        string = "bad encoding"
    return string


def get_page(book, size, pos, shift):
    text = ""
    chunk = ""
    # chunk = self.book[self.shift*x: self.shift * (1 + x)]
    text = book[pos: pos + shift]
    return chunk


def how_much_read(pos, size, shift):
    pages_read = ceil(pos / shift)
    pages_all = ceil(size / shift)
    return str(pages_read) + "/" + str(pages_all)


def how_much_percent_read(pos, size):
    return str(round(pos / size * 100, 2))


def find_text(book, text):
    lc = book.lower()
    pos = lc.find(text)
    return pos


def get_token():
    token = ""
    with open('TOKEN.txt', 'r') as file:
        token = file.read()
    return token


def user_not_found(id: int, user: telebot.types.User, bot: telebot.TeleBot):
    if not (id in userlist):
        if user.language_code == "ru":
            bot.send_message(id, "Пользователь не найден. Пожалуйста, введие /start для инициализации")
        else:
            bot.send_message(id, "User not found, Please enter /start for initialization")
        return True
    else:
        return False


def read_example():
    text = ""
    with open('example.txt') as file:
        text = file.read()
    return text


def timer(freq):
    import time
    timing = time.time()
    while True:
        if time.time() - timing > freq:
            timing = time.time()
            print(str(freq) + " seconds")


class Stickers:
    def __init__(self):
        self.id = []
        self.word = []
        self.hint = []
        self.size = 0
    def add(self, id_: str, word_: str = "", hint_: str = ""):
        self.id.append(id_)
        self.word.append(word_)
        self.hint.append(hint_)
        self.size += 1

    def get_w(self, word_: str):
        if word_ in self.word:
            i = self.word.index(word_)
            return self.id[i]
        else:
            return None

    def get_i(self, i: int):
        if i < self.size:
            return self.id[i]
        else:
            return None

# sticker pack
sp = Stickers()
sp.add("CAACAgIAAxkBAAELtnpl9VkhpuQvkThhwSy-IhpE68zt7wACMwEAAvcCyA87yuGU7tlOzTQE", "wolf")
sp.add("CAACAgIAAxkBAAELtoBl9Vwm3-_T4ITWdqMQsQQzwMcg9wACVQADs0poA9xNkuVgFL_oNAQ", "pinguin")
sp.add("CAACAgIAAxkBAAELt21l9cyAXWGoa9tfC3Vlut2S-1ljkgACUCMAApMYqUp6yGYHnhMy_DQE", "picabeer")
sp.add("CAACAgIAAxkBAAELt3Jl9c2F75STa0bPSjTgXFnf_QdOwwACbwoAAkKvaQABmbwY8P7C4jo0BA", "sadcat")
sp.add("CAACAgIAAxkBAAELt-Zl9eKiyE2NItV_9Bld9DIqsD0-mQACqAsAAulVBRgJlTzaJ96xHjQE", "captureworld")
sp.add("CAACAgIAAxkBAAELt-hl9eLQHhsJf2STOIvLsb-_YRb6KAAClQsAAulVBRg2DkTXlXO43TQE", "hz")
sp.add("CAACAgIAAxkBAAELt-xl9eMWjj_sm4KQ_25i93R0Q8x4agACQgEAAjDUnRG4DeX4EyUlwDQE", "begemot")
sp.add("CAACAgIAAxkBAAELt-5l9eP4J4IvH_nXMOE-n66tD7FWlwAC8hAAAoIAAbBKRNEbY9STXJQ0BA", "hellcat")
sp.add("CAACAgQAAxkBAAELt_hl9eXtZ-RA2XtlObXiQGkGiJXUIwACxQYAAlGMzwFko20gjdQVMDQE", "ы")
sp.add("CAACAgIAAxkBAAELuAJl9eeCIb5XHF_AsU4HKzMagzZkJgACCQADlMeUFc6-pV4r6sDDNAQ", "takblet")
sp.add("CAACAgIAAxkBAAELuBZl9ef9xkwDgGPgGhoJ-AVzy-VO2wACnAADnKO-D-ijomIItsQgNAQ", "chego")
sp.add("CAACAgIAAxkBAAELuBRl9efek05RUSW4zX-Zme2F8NQhAgACJAADdq4RAAGCkekfZbfX1TQE", "jewshiba")


