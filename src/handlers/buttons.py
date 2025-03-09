from telebot import TeleBot
from telebot import types
from src.modules import book_parser


def button_menu(bot: TeleBot, id: int, lang: str, splitted_text: list[str]):
    menu_list = ["Меню", "меню", "Menu", "menu"]

    # Inline Buttons here
    if any(x in splitted_text for x in menu_list):
        ru = ["Перейти на страницу", "Изменить размер страницы", "Найти фразу", "Прогресс", "Помощь",
              "Включить напоминания"]
        en = ["Change page number", "Change page size", "Looking for a phrase", "Progress", "Help",
              "Switch on reminder"]
        data = ["page_number", "page_size", "find_phrase", "state", "help", "reminder"]
        text = {True: ru, False: en}[lang == 'ru']

        imarkup = types.InlineKeyboardMarkup(row_width=1)
        for i in range(6):
            b = types.InlineKeyboardButton(text[i], callback_data=data[i])
            imarkup.add(b)

        text = {True: "Возможности читалки", False: "What I can do"}[lang == 'ru']
        bot.send_message(id, text, parse_mode='HTML', reply_markup=imarkup)
        return True
    return False


def button_next(bot: TeleBot, id: int, lang: str, splitted_text: list[str]):
    next_list = ["Далее", "далее", "Next", "next"]
    if any(x in splitted_text for x in next_list):
        text = book_parser.next_page(id)
        bot.send_message(id, text)
        return True
    return False