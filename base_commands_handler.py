from telebot import TeleBot
from telebot import types
import sql
import tools
import os

# TODO: more flexible commands for my usage


def debug(message: types.Message, bot: TeleBot):
    user = message.from_user
    id = user.id
    res = str(list(sql.get_data(id)))
    s = ' '.join(res)
    bot.reply_to(message, s)
    lang = sql.get_lang(id)



def check(message: types.Message, bot: TeleBot):

    lang = message.from_user.language_code
    ru, eng = "Бот включен", "Bot is working"
    bot.reply_to(message, {True: ru, False: eng}[lang == 'ru'])

    # bot.send_sticker(message.from_user.id, tools.sp.get_i(0))



def start(message: types.Message, bot: TeleBot):
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

    isNew = not (id in tools.userlist)
    if isNew:
        folder = os.path.join("User", str(id))
        if not os.path.exists(folder):
            os.makedirs(folder)
        sql.add_new_user(id)
        tools.userlist.append(id)
        tools.log("user " + str(id) + " has been created")

        f = open((os.path.join(folder, "userinfo.txt")), "w")
        f.write("First name: " + str(user.first_name) + "\n")
        f.write("Last name: " + str(user.last_name) + "\n")
        f.write("username: " + str(user.username) + "\n")
        f.close()

    sql.update_text(id, field='language', value=user.language_code)


def help(message: types.Message, bot: TeleBot):
    id = message.chat.id
    lang = sql.get_lang(id)
    ru = '''Бот-помощник для чтения книг по кусочкам. Введите команду /start для создания \
настроек пользователя/ обновления кнопки меню. Затем загрузите текстовый файл в формате *.txt. \
Для загрузки примера книги введите команду /example. Нажмите кнопку "Далее" для перелистывания страниц. \
В меню можно настроить размер страницы, но не более 4000 символов (ограничения Телеграма) и прочие мелочи. 
Все претензии присылайте на адрес: «Спортлото»: 109316, Москва, Волгоградский проспект, д. 43, корп. 3
    '''
    en = ''' Your bot-helper to read books by chunks. \
Enter /start to initialize your profile or update menu buttons. \
Upload *.txt file to start reading. For setting an example book, enter /example. \
You can set different things in menu. Press "Next" to turn a page.
    '''
    text = {True: ru, False: en}[lang == 'ru']
    bot.send_message(id, text)


def swap_lang(message: types.Message, bot: TeleBot):
    id = message.from_user.id
    lang = sql.get_lang(id)
    if lang == 'en':
        sql.update_text(id, field='language', value='ru')
        bot.send_message(id, "русский")
    else:
        sql.update_text(id, field='language', value='en')
        bot.send_message(id, "english")