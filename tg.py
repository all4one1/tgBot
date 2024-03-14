# TODO:
#   examples
#   check if non active
#   refactoring

import telebot
import os
import reminder
import book_parser
import tools
import sql
import urllib.request
from telebot import types
from threading import Thread

print("start")
tools.init()
TOKEN = tools.get_token()
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
userlist = sql.get_user_id_list()
bot_info = bot.get_me()


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
    user = message.from_user
    bot.send_message(id, user.language_code)
    sql.update_text(id, field='language', value=lang)


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
    if isNew:
        folder = os.path.join("User", str(id))
        if not os.path.exists(folder):
            os.makedirs(folder)
        sql.add_new_user(id)
        userlist.append(id)
        tools.log("user " + str(id) + " has been created")

        f = open((os.path.join(folder, "userinfo.txt")), "w")
        f.write("First name: " + str(user.first_name) + "\n")
        f.write("Last name: " + str(user.last_name) + "\n")
        f.write("username: " + str(user.username) + "\n")
        f.close()

    sql.update_text(id, field='language', value=user.language_code)


@bot.message_handler(commands=["next"])
def next_page(message):
    user = message.from_user
    id = user.id
    if user_not_found(user, id):
        return

    text = book_parser.next_page(id)
    bot.send_message(id, text)


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
    input = message.text
    text = book_parser.set_page_number(id, input)
    bot.send_message(id, text)


def set_page_size(message):
    id = message.chat.id
    input = message.text
    text = book_parser.set_page_size(id, input)
    bot.send_message(id, text)


def set_page_by_phrase(message):
    id = message.chat.id
    phrase = message.text
    text = book_parser.set_page_by_phrase(id, phrase)
    bot.send_message(id, text)


def show_state(message):
    id = message.chat.id
    text = book_parser.show_state(id)
    bot.send_message(id, text)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    id = call.message.chat.id
    mes = call.message
    lang = call.from_user
    command = call.data.split()

    if call.data == 'page_number':
        ru, eng = "Введите номер страницы", "Enter the page number"
        bot.send_message(id, {True: ru, False: eng}[lang == 'ru'])
        bot.register_next_step_handler(mes, set_page_number)
    if call.data == 'page_size':
        ru, eng = "Введи размер страницы в символах, не более 4000", "Enter the page size, not more 4000 symbols"
        bot.send_message(id, {True: ru, False: eng}[lang == 'ru'])
        bot.register_next_step_handler(mes, set_page_size)
    if call.data == 'find_phrase':
        ru, eng = "Введите искомую фразу", "Enter the phrase to look for"
        bot.send_message(id, {True: ru, False: eng}[lang == 'ru'])
        bot.register_next_step_handler(mes, set_page_by_phrase)
    if call.data == "state":
        show_state(mes)
    if call.data == "help":
        get_help(mes)
    if call.data == "reminder":
        reminder.set_reminder(bot, mes)

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


print("new thread")
thread = Thread(target=reminder.start, args=[bot])
thread.start()


print("polling")
bot.infinity_polling(timeout=10001)
