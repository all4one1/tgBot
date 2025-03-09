from src import tools
from src import sql
import urllib.request
from telebot import TeleBot
from telebot.types import Message


# TODO: additional filters: size, type of a file
def obtained(message: Message, bot: TeleBot):
    user = message.from_user
    id = user.id

    isNew = not (id in tools.userlist)
    if isNew == True:
        lang = user.language_code
        text = {True: "Ошибка, введите /start", False: "Error, you have not /start'ed"}[lang == 'ru']
        bot.send_message(id, text)
        return

    # bot.reply_to(message, message.document)
    doc = message.document
    file = bot.get_file(doc.file_id)
    link = 'https://api.telegram.org/file/bot' + tools.TOKEN + '/' + file.file_path
    file_name = str(doc.file_name)
    current_path = tools.get_current_path(id)
    response = urllib.request.urlretrieve(link, current_path)
    f = open(current_path, "r")
    if f.readable() == True:
        lang = sql.get_lang(id)
        text = {True: "Файл получен", False: "File has been received"}[lang == 'ru']
        bot.reply_to(message, text)
        sql.update(id=id, field='isOpen', value=1)
        sql.update(id=id, field='position', value=0)