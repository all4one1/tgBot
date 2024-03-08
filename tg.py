import telebot
import os
import tools
import sql
import urllib.request
from telebot import types


TOKEN = tools.get_token()
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

tools.init()
userlist = sql.get_user_id_list()

print("bot started")
bot_info = bot.get_me()


@bot.message_handler(commands=["debug"])
def response(message):
    user = message.from_user
    id = user.id
    res = str(list(sql.get_data(id)))
    s = ' '.join((res))
    bot.reply_to(message, s)

@bot.message_handler(commands=["check"])
def response(message):
    bot.reply_to(message, "Бот включен")


@bot.message_handler(commands=["start"])
def beginning(message):
    user = message.from_user
    id = user.id
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button_next = types.KeyboardButton("⏩ Далее")
    button_menu = types.KeyboardButton("📘 Меню")
    markup.add(button_menu, button_next)
 
    if user.language_code == "ru":
        bot.send_message(id, "Здравствуй, дорогой друг", reply_markup=markup)
    else:
        bot.send_message(id, "Hello, dear friend", reply_markup=markup)    
    
    folder = os.path.join("User",str(id))
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    isNew = not (id in userlist)
    if isNew == True:
        sql.add_new_user(id)
        userlist.append(id)
        tools.log("user " + str(id) + " has been created")
        
        f = open((os.path.join(folder,"userinfo.txt")),"w")
        f.write("First name: " + str(user.first_name) + "\n")
        f.write("Last name: " + str(user.last_name)+ "\n")
        f.write("username: " + str(user.username)+ "\n")  
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
            bot.send_message(id, "Файла не обнаружено. Пожалуйста, попробуйте загрузить снова")
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
    sql.update(id = id, field = "position", value = end_pos)

@bot.message_handler(content_types=["document"])
def obtained(message):
    user = message.from_user
    id = user.id
    
    isNew = not (id in userlist)
    if isNew == True:
        bot.send_message(id, "Error, you have not /started")
        
        
    #bot.reply_to(message, message.document)
    doc = message.document
    file = bot.get_file(doc.file_id)
    link = 'https://api.telegram.org/file/bot'+TOKEN+'/'+ file.file_path
    file_name = str(doc.file_name)
    current_path = tools.get_current_path(id)
    response = urllib.request.urlretrieve(link, current_path)
    f = open(current_path, "r")
    if f.readable() == True:
        bot.reply_to(message, "file has been received")
        sql.update(id = id, field = 'isOpen', value = 1)
        sql.update(id = id, field = 'position', value = 0)
   
@bot.message_handler(commands=["help"])
def get_help(message, language_code = 'ru'):
    id = message.chat.id
    #if language_code == 'ru':
    text = '''Это бот. Бот-читалка. Сам за тебя читать он не будет. Формат-аудио книг это в другое место. 
Идея данного бота - читать самому. Сам читаешь - глубже все понимаешь. Есть какие-то исследования, что читать большие книги - тяжело. Но когда книжка разбита на мелкие фрагметы - тот же самый объем текста по частям "поглощается" в разы быстрее. 
А еще, в телеграм многие заходят по всякой ерунде, листая (по большому счету) бесполезную персональную ленту. А так глядишь и книжку какую умную мимо ходом осилишь (пускай и не быстро).
Если вы еще того не сделали, введите команду /start для создания настроек пользователя. Затем загрузите текстовый файл в формате *.txt.
Нажмите кнопку "Далее" для перелистывания страниц. В меню можно настроить размер страницы, но не более 4000 символов (ограничения Телеграма)
Все претензии присылайте на адрес: «Спортлото»: 109316, Москва, Волгоградский проспект, д. 43, корп. 3
'''
    bot.send_message(id, text)

@bot.message_handler(content_types=["text"])
def inline_buttons(message):
    user = message.from_user
    id = user.id 
    if user_not_found(user, id):
        return
    isOpen, pos, shift, freq = sql.get_data(id)    

    my_text = message.text
    split_text = my_text.split(" ")
    
    menu_list = ["Меню", "меню", "Menu", "menu"]
    if any(x in split_text for x in menu_list):
        imarkup = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton("Номер страницы", callback_data = "page_number")
        b2 = types.InlineKeyboardButton("Размер страницы", callback_data = "page_size")
        b3 = types.InlineKeyboardButton("Найти фразу", callback_data = "find_phrase")
        b4 = types.InlineKeyboardButton("Прочитано", callback_data = "state")
        b5 = types.InlineKeyboardButton("Помощь", callback_data = "help")
        imarkup.add(b1,b2,b3,b4,b5)
        bot.send_message(id,"Возможности читалки", parse_mode='HTML', reply_markup=imarkup)

    next_list = ["Далее", "далее", "Next", "next"] 
    if any(x in split_text for x in next_list):
        next_page(message)
        
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    id = call.message.chat.id
    mes = call.message
    language_code = call.from_user.language_code
    
    
    if call.data == 'page_number':
        bot.send_message(id, "Введите номер страницы")
        bot.register_next_step_handler(mes, set_page_number)
    if call.data == 'page_size':
        bot.send_message(id, "Введи размер страницы в символах, не более 4000")
        bot.register_next_step_handler(mes, set_page_size)
    if call.data == 'find_phrase':
        bot.send_message(id, "Введите искомую фразу")
        bot.register_next_step_handler(mes, set_page_by_phrase)     
    if call.data == "state":
        show_state(mes)    
    if call.data == "help":
        get_help(mes)

def set_page_number(message):
    id = message.chat.id   
    isOpen, pos, shift, freq = sql.get_data(id)
    if isOpen == 1:     
        n = tools.to_int(message.text)
        if n == -1:
            bot.send_message(message.chat.id, "Вы ввели хуйню")
        else:
            pos = (n) * shift
            sql.update(id = id, field = "position", value = pos)
            path = tools.get_current_path(id)
            book = tools.get_book(path)
            size_N = len(book)
            text = "Страница: " +  tools.how_much_read(pos, size_N, shift)
            bot.send_message(id, text)                       

def set_page_size(message):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    n = tools.to_int(message.text)

    if n == -1:
        bot.send_message(message.chat.id, "Хули ты вводишь")
    elif n > 4000:
        bot.send_message(message.chat.id, "Ты тупой?")        
    elif n < 20:
        bot.send_message(message.chat.id, "Ха-ха-ха, как смешно")
    else:
        sql.update(id = id, field = "pagesize", value = n)        
        bot.send_message(id, "Текущий размер страницы " + str(n) + " символов")

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
                #if user.language_code == "ru":
                    bot.send_message(id, "Ничего не найдено")
                #else:
                    #bot.send_message(id, "Not found")                  
            else:  
                size_N = len(book)
                read = tools.how_much_read(pos, size_N, shift)
                end_pos = pos + shift
                text = book[pos: end_pos] + "\n" + read
                bot.send_message(id, text)
                sql.update(id = id, field = "position", value = end_pos)   
    
def show_state(message):
    id = message.chat.id
    isOpen, pos, shift, freq = sql.get_data(id)
    if isOpen == 1:
        path = tools.get_current_path(id)
        book = tools.get_book(path)        
        size_N = len(book)
        per = pos/size_N*100

        pages_read = tools.how_much_read(pos, size_N, shift)
        percent = tools.how_much_percent_read(pos, size_N)
        
        bot.send_message(id, "Прочитано: " + percent + " %, или " + pages_read + " стр.")
        #if user.language_code == "ru":
        #   bot.send_message(id, "Прочитано: " + percent + " %, или " + pages_read + " стр.")
        #else:
        #    bot.send_message(id, "Finished: " + percent + " %, or " + pages_read + " pp.")
        
    else:
        bot.send_message(id, "Вы еще не загрузили файл")

def user_not_found(user, id):
    if not(id in userlist):
        if user.language_code == "ru":
            bot.send_message(id, "Пользователь не найден. Пожалуйста, введие /start для инициализации")
        else:
            bot.send_message(id, "User not found, Please enter /start for initialization")
        return True
    else:
        return False 
 
bot.infinity_polling(timeout = 10001)





