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
                    text += "\nIt's reminder!"
                    bot.send_message(id, text)


def set_reminder(bot: telebot.TeleBot, message: types.Message):
    id = message.chat.id
    lang = message.from_user.language_code
    isOpen, pos, shift, freq = sql.get_data(id)

   # if lang == 'ru':
   #     imarkup = types.InlineKeyboardMarkup(row_width=2)
   #     b1 = types.InlineKeyboardButton("1 day", callback_data="help")
   #     b2 = types.InlineKeyboardButton("12 hours", callback_data="state")
   #     imarkup.add(b1, b2)
   #     bot.send_message(id, "Как частно присылать фрагмент", parse_mode='HTML', reply_markup=imarkup)
   # else:

    imarkup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("1 day", callback_data="freq 86400")
    b2 = types.InlineKeyboardButton("12 hours", callback_data="freq 43200")
    b3 = types.InlineKeyboardButton("8 hours", callback_data="freq 28800")
    b4 = types.InlineKeyboardButton("4 hours", callback_data="freq 14400")
    b5 = types.InlineKeyboardButton("2 hours", callback_data="freq 7200")
    b6 = types.InlineKeyboardButton("1 hour", callback_data="freq 3600")
    imarkup.add(b1, b2, b3, b4, b5, b6)
    bot.send_message(id, "How often would you like to get a text?", parse_mode='HTML', reply_markup=imarkup)

