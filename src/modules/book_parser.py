import time
from src import tools
from src import sql
from telebot import TeleBot
from telebot.types import Message


def next_page(id):
    path = tools.get_current_path(id)
    book = tools.get_book(path)

    isOpen, pos, shift, freq = sql.get_data(id)
    lang = sql.get_lang(id)
    if isOpen == 0:
        ru, eng = ("Файл не обнаружен. Пожалуйста, попробуйте загрузить снова",
                   "File not found. Please, try uploading again")
        message = ({True: ru, False: eng}[lang == 'ru'])
        sql.update(id, field='lastcall', value=0)
        return message

    size_N = len(book)
    if pos > size_N:
        sql.update(id, field='lastcall', value=0)
        ru, eng = "Текст закончился", "Text is over"
        message = ({True: ru, False: eng}[lang == 'ru'])
        return message

    end_pos = pos + shift
    pages_read = tools.how_much_read(end_pos, size_N, shift)
    text = book[pos: end_pos] + "\n" + pages_read
    sql.update(id=id, field='position', value=end_pos)
    sql.update(id=id, field='lastcall', value=int(time.time()))
    return text


def set_page_number(message: Message, bot: TeleBot):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    lang = sql.get_lang(id)
    if isOpen == 1:
        n = tools.to_int(message.text)
        if n == -1:
            ru, eng = "Ты че вводишь, алё", "It is nonsense"
            text = {True: ru, False: eng}[lang == 'ru']
        else:
            pos = n * shift
            sql.update(id=id, field="position", value=pos)
            path = tools.get_current_path(id)
            book = tools.get_book(path)
            size_N = len(book)
            ru, eng = "Страница ", "Page "
            text = {True: ru, False: eng}[lang == 'ru'] + tools.how_much_read(pos, size_N, shift)
        bot.send_message(id, text)


def set_page_size(message: Message, bot: TeleBot):
    id = message.chat.id
    # isOpen, pos, shift, freq = sql.get_data(id)
    lang = sql.get_lang(id)
    n = tools.to_int(message.text)

    if n == -1:
        ru, eng = "Доброе утро, че вводишь?", "Wtf are you trying to do?"
    elif n > 4000:
        ru, eng = "Вы читать не умеете? (Зачем вам этот бот?) 4000 - максимум", "Can you read? 4000 is the maximum"
    elif n < 20:
        ru, eng = "Ха-ха-ха, очень смешно", "Yeah, very funny"
    else:
        sql.update(id=id, field="pagesize", value=n)
        ru, eng = ("Текущий размер страницы " + str(n) + " символов",
                   "Current page size is " + str(n) + " symbols")

    text = {True: ru, False: eng}[lang == 'ru']
    bot.send_message(id, text)


def set_page_by_phrase(message: Message, bot: TeleBot):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    lang = sql.get_lang(id)
    if isOpen == 1:
        w = message.text.lower()

        if len(w) > 1:
            path = tools.get_current_path(id)
            book = tools.get_book(path)
            lc = book.lower()
            pos = lc.find(w)

            if pos == -1:
                text = {True: "Ничего не найдено", False: "Not found"}[lang == 'ru']

            else:
                size_N = len(book)
                read = tools.how_much_read(pos, size_N, shift)
                end_pos = pos + shift
                text = book[pos: end_pos] + "\n" + read
                sql.update(id=id, field="position", value=end_pos)

            bot.send_message(id, text)

def show_state(message: Message, bot: TeleBot):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    lang = sql.get_lang(id)
    if isOpen == 1:
        path = tools.get_current_path(id)
        book = tools.get_book(path)
        size_N = len(book)
        # per = pos / size_N * 100
        pages_read = tools.how_much_read(pos, size_N, shift)
        percent = tools.how_much_percent_read(pos, size_N)

        ru, eng = ("Прочитано: " + percent + " %, или " + pages_read + " стр.",
                   "You have read: " + percent + " %, or " + pages_read + " pages.")
        text = {True: ru, False: eng}[lang == 'ru']

    else:
        ru, eng = "Вы еще не загрузили файл", "You have not yet uploaded a file"
        text = {True: ru, False: eng}[lang == 'ru']

    bot.send_message(id, text)
