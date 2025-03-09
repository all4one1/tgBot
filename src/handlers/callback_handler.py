from telebot import TeleBot
from telebot.types import CallbackQuery
from src.modules import book_parser
from src import sql
from src.handlers import base_commands_handler
from src.modules import reminder


def callbacks(call: CallbackQuery, bot: TeleBot):
    id = call.message.chat.id
    mes = call.message
    lang = sql.get_lang(id)
    command = call.data.split()

    if call.data == 'page_number':
        ru, eng = "Введите номер страницы", "Enter the page number"
        bot.send_message(id, {True: ru, False: eng}[lang == 'ru'])
        bot.register_next_step_handler(mes, book_parser.set_page_number, bot)
    if call.data == 'page_size':
        ru, eng = "Введи размер страницы в символах, не более 4000", "Enter the page size, not more 4000 symbols"
        bot.send_message(id, {True: ru, False: eng}[lang == 'ru'])
        bot.register_next_step_handler(mes, book_parser.set_page_size, bot)
    if call.data == 'find_phrase':
        ru, eng = "Введите искомую фразу", "Enter the phrase to look for"
        bot.send_message(id, {True: ru, False: eng}[lang == 'ru'])
        bot.register_next_step_handler(mes, book_parser.set_page_by_phrase, bot)
    if call.data == "state":
        book_parser.show_state(mes, bot)
    if call.data == "help":
        base_commands_handler.help(mes, bot)
    if call.data == "reminder":
        reminder.set_reminder(mes, bot)
    if len(command) > 1:
        if command[0] == "freq":
            freq = int(command[1])
            sql.update(id, field='frequency', value=freq)
            ru, en = (f"Частота сообщений: {freq} сек.", f"frequency set to {freq} seconds")
            bot.send_message(id, {True: ru, False: en}[lang == 'ru'])


