import time
import telebot
from telebot import types
import sql
import book_parser
import tools


def start(bot: telebot.TeleBot):
    while True:
        time.sleep(10)
        idlist = sql.get_user_id_list()
        for id in idlist:
            isOpen, pos, shift, freq = sql.get_data(id)
            lang = sql.get_lang(id)
            if freq > 0:
                now = int(time.time())
                last = sql.get_last(id)
                if last == 0:
                    # sql.update(id=id, field='lastcall', value=int(time.time()))
                    continue
                dif = now - last
                if dif > freq:
                    text = book_parser.next_page(id)
                    add = {True: "\n(Напоминание)", False: "\n (... reminded!)"}[lang=='ru']
                    text += add
                    bot.send_message(id, text)


def set_reminder(message: types.Message, bot: telebot.TeleBot):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    lang = sql.get_lang(id)

    min = lambda s: s * 60
    hour = lambda s: s * min(60)
    day = lambda s: s * hour(24)

    ru = ["1 неделя", "1 день", "12 часов", "8 часов", "4 часа", "2 часа", "1 час", "Никогда"]
    en = ["1 week", "1 day", "12 hours", "8 hours", "4 hours", "2 hours", "1 hour", "Never"]
    text = {True: ru, False: en}[lang == 'ru']
    values = [day(7), day(1), hour(12), hour(8), hour(4), hour(2), hour(1), 0]

    ls = []
    for i in range(8):
        button = types.InlineKeyboardButton(text[i], callback_data=f"freq {values[i]}")
        ls.append(button)

    imarkup = types.InlineKeyboardMarkup(keyboard=[ls[0:4], ls[4:8]])

    text = {True: "Как часто изволите напоминать?", False: "How often would you like to receive a text?"}[lang == 'ru']
    bot.send_message(id, text, parse_mode='HTML', reply_markup=imarkup)

