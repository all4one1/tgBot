import telebot
import os
import tools
import sql
import urllib.request
from telebot import types
from threading import Thread
import time
import schedule

tools.init()
TOKEN = tools.get_token()
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=False)
userlist = sql.get_user_id_list()
bot_info = bot.get_me()
print("bot started")


@bot.message_handler(commands=["debug"])
def response(message):
    user = message.from_user
    id = user.id
    res = str(list(sql.get_data(id)))
    s = ' '.join(res)
    bot.reply_to(message, s)


@bot.message_handler(commands=["check"])
def response(message):
    lang = message.from_user.language_code
    ru, eng = "Бот включен", "Bot is on"
    bot.reply_to(message, {True: ru, False: eng}[lang == 'ru'])
    id = message.chat.id
    chat = bot.get_chat(id)
    #print(type(message))
    #print(chat)
    #print(type(chat))

@bot.message_handler(commands=["start"])
def beginning(message):
    user = message.from_user
    id = user.id

    # main buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user.language_code == "ru":
        button_next = types.KeyboardButton("⏩ Далее")
        button_menu = types.KeyboardButton("📘 Меню")
    else:
        button_next = types.KeyboardButton("⏩ Next")
        button_menu = types.KeyboardButton("📘 Menu")
    markup.add(button_menu, button_next)

    # greeting message
    if user.language_code == "ru":
        bot.send_message(id, "Здравствуй, дорогой друг. Загрузи *.txt файл, чтобы начать", reply_markup=markup)
    else:
        bot.send_message(id, "Hello, dear friend. Upload a *.txt file to get started", reply_markup=markup)


    isNew = not (id in userlist)
    if isNew == True:
        folder = os.path.join("User", str(id))
        if not os.path.exists(folder):
            os.makedirs(folder)

        sql.add_new_user(id)
        sql.update(id, field='language', value=user.language_code)
        userlist.append(id)
        tools.log("user " + str(id) + " has been created")

        f = open((os.path.join(folder, "userinfo.txt")), "w")
        f.write("First name: " + str(user.first_name) + "\n")
        f.write("Last name: " + str(user.last_name) + "\n")
        f.write("username: " + str(user.username) + "\n")
        f.close()


@bot.message_handler(commands=["next"])
def next_page(message):
    user = message.from_user
    id = user.id
    if user_not_found(user, id):
        return

    isOpen, pos, shift, freq = sql.get_data(id)
    if isOpen == 0:
        if user.language_code == "ru":
            bot.send_message(id, "Файл не обнаружен. Пожалуйста, попробуйте загрузить снова")
        else:
            bot.send_message(id, "File not found. Please, try uploading again")
        return

    path = tools.get_current_path(id)
    book = tools.get_book(path)

    size_N = len(book)
    if pos > size_N:
        if user.language_code == "ru":
            bot.send_message(id, "Текст закончился")
        else:
            bot.send_message(id, "Text is over")
        return

    end_pos = pos + shift
    pages_read = tools.how_much_read(end_pos, size_N, shift)

    text = book[pos: end_pos] + "\n" + pages_read
    bot.send_message(id, text)
    sql.update(id=id, field="position", value=end_pos)





@bot.message_handler(content_types=["document"])
def obtained(message):
    user = message.from_user
    id = user.id

    isNew = not (id in userlist)
    if isNew == True:
        bot.send_message(id, "Error, you have not /started")

    # bot.reply_to(message, message.document)
    doc = message.document
    file = bot.get_file(doc.file_id)
    link = 'https://api.telegram.org/file/bot' + TOKEN + '/' + file.file_path
    file_name = str(doc.file_name)
    current_path = tools.get_current_path(id)
    response = urllib.request.urlretrieve(link, current_path)
    f = open(current_path, "r")
    if f.readable() == True:
        bot.reply_to(message, "file has been received")
        sql.update(id=id, field='isOpen', value=1)
        sql.update(id=id, field='position', value=0)


@bot.message_handler(commands=["help"])
def get_help(message, language_code='ru'):
    id = message.chat.id
    text = ""
    if language_code == 'ru':
        text = '''Это бот-читалка. Сам за тебя читать он не будет. Есть какие-то исследования, что читать большие книги - тяжело. Но когда книжка разбита на мелкие фрагметы - тот же самый объем текста по частям "поглощается" в разы быстрее. 
А еще, в телеграм многие заходят по всякой ерунде, листая (по большому счету) бесполезную персональную ленту. А так глядишь и книжку какую умную мимо ходом осилишь (пускай и не быстро).
Если вы еще того не сделали, введите команду /start для создания настроек пользователя. Затем загрузите текстовый файл в формате *.txt.
Нажмите кнопку "Далее" для перелистывания страниц. В меню можно настроить размер страницы, но не более 4000 символов (ограничения Телеграма)
Все претензии присылайте на адрес: «Спортлото»: 109316, Москва, Волгоградский проспект, д. 43, корп. 3
'''
    else:
        text = ''' upload *.txt file to start
                '''
    bot.send_message(id, text)


@bot.message_handler(content_types=["text"])
def inline_buttons(message):
    user = message.from_user
    id = user.id
    lang = user.language_code
    if user_not_found(user, id):
        return
    isOpen, pos, shift, freq = sql.get_data(id)

    my_text = message.text
    split_text = my_text.split(" ")

    menu_list = ["Меню", "меню", "Menu", "menu"]
    if any(x in split_text for x in menu_list):
        if lang == 'ru':
            imarkup = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton("Перейти на страницу", callback_data="page_number")
            b2 = types.InlineKeyboardButton("Изменить размер страницы.", callback_data="page_size")
            b3 = types.InlineKeyboardButton("Найти фразу", callback_data="find_phrase")
            b4 = types.InlineKeyboardButton("Прогресс", callback_data="state")
            b5 = types.InlineKeyboardButton("Помощь", callback_data="help")
            b6 = types.InlineKeyboardButton("Switch on reminder", callback_data="reminder")
            imarkup.add(b1, b2, b3, b4, b5, b6)
            bot.send_message(id, "Возможности читалки", parse_mode='HTML', reply_markup=imarkup)
        else:
            imarkup = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton("Change page number", callback_data="page_number")
            b2 = types.InlineKeyboardButton("Change page size", callback_data="page_size")
            b3 = types.InlineKeyboardButton("Looking for a phrase", callback_data="find_phrase")
            b4 = types.InlineKeyboardButton("Progress", callback_data="state")
            b5 = types.InlineKeyboardButton("Help", callback_data="help")
            b6 = types.InlineKeyboardButton("Switch on reminder", callback_data="reminder")
            imarkup.add(b1, b2, b3, b4, b5, b6)
            bot.send_message(id, "What I can do", parse_mode='HTML', reply_markup=imarkup)

    next_list = ["Далее", "далее", "Next", "next"]
    if any(x in split_text for x in next_list):
        next_page(message)



def set_page_number(message):
    id = message.chat.id
    lang = message.from_user.language_code
    isOpen, pos, shift, freq = sql.get_data(id)
    if isOpen == 1:
        n = tools.to_int(message.text)
        if n == -1:
            ru, eng = "Ты че вводишь, алё", "It is nonsense"
            bot.send_message(message.chat.id, {True: ru, False: eng}[lang == 'ru'])
        else:
            pos = n * shift
            sql.update(id=id, field="position", value=pos)
            path = tools.get_current_path(id)
            book = tools.get_book(path)
            size_N = len(book)
            ru, eng = "Страница ", "Page "
            text = {True: ru, False: eng}[lang == 'ru'] + tools.how_much_read(pos, size_N, shift)
            bot.send_message(id, text)


def set_page_size(message):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    n = tools.to_int(message.text)
    lang = message.from_user.language_code
    if n == -1:
        ru, eng = "Доброе утро, че вводишь?", "Wtf are you trying to do?"
        bot.send_message(message.chat.id, {True: ru, False: eng}[lang == 'ru'])
    elif n > 4000:
        ru, eng = "Вы читать не умеете? (Зачем вам этот бот?) 4000 - максимум", "Can you read? 4000 is the maximum"
        bot.send_message(message.chat.id, {True: ru, False: eng}[lang == 'ru'])
    elif n < 20:
        ru, eng = "Ха-ха-ха, очень смешно", "Yeah, very funny"
        bot.send_message(message.chat.id, {True: ru, False: eng}[lang == 'ru'])
    else:
        sql.update(id=id, field="pagesize", value=n)
        ru, eng = ("Текущий размер страницы " + str(n) + " символов",
                   "Current page size is " + str(n) + " symbols")
        bot.send_message(message.chat.id, {True: ru, False: eng}[lang == 'ru'])

def set_page_by_phrase(message):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)

    if isOpen == 1:
        w = (message.text).lower()

        if len(w) > 1:
            path = tools.get_current_path(id)
            book = tools.get_book(path)
            lc = book.lower()
            pos = lc.find(w)

            if pos == -1:
                # if user.language_code == "ru":
                bot.send_message(id, "Ничего не найдено")
            # else:
            # bot.send_message(id, "Not found")
            else:
                size_N = len(book)
                read = tools.how_much_read(pos, size_N, shift)
                end_pos = pos + shift
                text = book[pos: end_pos] + "\n" + read
                bot.send_message(id, text)
                sql.update(id=id, field="position", value=end_pos)


def show_state(message):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    if isOpen == 1:
        path = tools.get_current_path(id)
        book = tools.get_book(path)
        size_N = len(book)
        per = pos / size_N * 100

        pages_read = tools.how_much_read(pos, size_N, shift)
        percent = tools.how_much_percent_read(pos, size_N)

        bot.send_message(id, "Прочитано: " + percent + " %, или " + pages_read + " стр.")
        # if user.language_code == "ru":
        #   bot.send_message(id, "Прочитано: " + percent + " %, или " + pages_read + " стр.")
        # else:
        #    bot.send_message(id, "Finished: " + percent + " %, or " + pages_read + " pp.")

    else:
        bot.send_message(id, "Вы еще не загрузили файл")


def set_reminder(message):
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



@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    id = call.message.chat.id
    mes = call.message
    lang = call.from_user
    command = call.data.split()

    if call.data == 'page_number':
        ru, eng = "Введите номер страницы", "Enter the page number"
        bot.send_message(id, {True: ru, False: eng} [lang == 'ru'])
        bot.register_next_step_handler(mes, set_page_number)
    if call.data == 'page_size':
        ru, eng = "Введи размер страницы в символах, не более 4000", "Enter the page size, not more 4000 symbols"
        bot.send_message(id, {True: ru, False: eng} [lang == 'ru'])
        bot.register_next_step_handler(mes, set_page_size)
    if call.data == 'find_phrase':
        ru, eng = "Введите искомую фразу", "Enter the phrase to look for"
        bot.send_message(id, {True: ru, False: eng} [lang == 'ru'])
        bot.register_next_step_handler(mes, set_page_by_phrase)
    if call.data == "state":
        show_state(mes)
    if call.data == "help":
        get_help(mes)
    if call.data == "reminder":
        set_reminder(mes)

    if len(command) > 1:
        if command[0] == "freq":
            freq = int(command[1])
            sql.update(id, field='frequency', value=freq)
            bot.send_message(id, "frequency set to " + str(freq) + " seconds")



def user_not_found(user, id):
    if not (id in userlist):
        if user.language_code == "ru":
            bot.send_message(id, "Пользователь не найден. Пожалуйста, введие /start для инициализации")
        else:
            bot.send_message(id, "User not found, Please enter /start for initialization")
        return True
    else:
        return False

def lang_text(lang, ru, eng):
    if lang == 'ru':
        return ru
    else:
        return eng



bot.infinity_polling(timeout=10001)
