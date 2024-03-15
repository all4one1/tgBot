from telebot import TeleBot
from telebot import types
import sql
import tools
import os


def register_all(bot: TeleBot):
    bot.register_message_handler(debug, commands=["debug"], pass_bot=True)
    bot.register_message_handler(check, commands=["check"], pass_bot=True)


def debug(message: types.Message, bot: TeleBot):
    user = message.from_user
    id = user.id
    res = str(list(sql.get_data(id)))
    s = ' '.join(res)
    bot.reply_to(message, s)
    lang = sql.get_lang(id)
    if lang == 'en':
        sql.update_text(id, field='language', value='ru')
        bot.send_message(id, "русский")
    else:
        sql.update_text(id, field='language', value='en')
        bot.send_message(id, "english")
    print(sql.get_lang(id))

def check(message: types.Message, bot: TeleBot):
    lang = message.from_user.language_code
    ru, eng = "Бот включен", "Bot is working"
    bot.reply_to(message, {True: ru, False: eng}[lang == 'ru'])
    text = {True: "Ошибка, введите /start", False: "Error, you have not /start'ed"}[lang == 'ru']
    bot.send_message(message.from_user.id, text)


def help(message: types.Message, bot: TeleBot):
    id = message.chat.id
    lang = sql.get_lang(id)
    ru ='''Бот-помощник для чтения книг по кусочкам. 
    Ввведите команду /start для создания настроек пользователя. Затем загрузите текстовый файл в формате *.txt.
    Нажмите кнопку "Далее" для перелистывания страниц. В меню можно настроить размер страницы, но не более 4000 символов (ограничения Телеграма)
    Все претензии присылайте на адрес: «Спортлото»: 109316, Москва, Волгоградский проспект, д. 43, корп. 3
    '''
    en = ''' Your bot-helper to read books by chunks. Upload *.txt file to start.'''
    text = {True: ru, False: en}[lang == 'ru']
    bot.send_message(id, text)