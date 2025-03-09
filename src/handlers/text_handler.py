import telebot

from src import tools
from src import sql
from telebot import TeleBot
from telebot import types
from src.handlers import buttons
from src.modules import book_parser


# TODO: do not proceed if one function is invoked (i.e. one condition is satisfied)
def process_any_text(message: types.Message, bot: TeleBot):
    user = message.from_user
    id = user.id
    if tools.user_not_found(id, user, bot):
        return
    lang = sql.get_lang(id)
    splitted_text = message.text.split(" ")

    # pressed buttons generate a text message
    # then it is processed by the next functions
    if buttons.button_menu(bot, id, lang, splitted_text):
        return
    if buttons.button_next(bot, id, lang, splitted_text):
        return

    why_reading(bot, id, lang, message.text)


def why_reading(bot: TeleBot, id: int, lang: str, text: str):
    why_list = ["зачем читать", "читать зачем", "зачем надо читать", "зачем читать надо",
                "почему я должен читать", "нахуй читать", "нахуя читать"]

    ls = []
    ls.append((tools.sp.get_w("picabeer"), "А чиво? Пивко что ли только одно глушить?"))
    ls.append((tools.sp.get_w("wolf"), "Будь умным, епт!"))
    ls.append((tools.sp.get_w("sadcat"), "Не расстраивай котика, читай книжки"))
    ls.append((tools.sp.get_w("captureworld"), ""))
    ls.append((tools.sp.get_w("hz"), ""))
    ls.append((tools.sp.get_w("begemot"), "уу сюк, не зли бегемотика, читай книги!"))
    ls.append((tools.sp.get_w("ы"), "Штоб быть граматнЫм!"))
    ls.append((tools.sp.get_w("takblet"), "Так блэт, что еще за вопросы?!"))
    ls.append((tools.sp.get_w("chego"), ""))
    ls.append((tools.sp.get_w("jewshiba"), "Евреи тысячелетиями на***ли гоев. "
                                           "Потому что книги читали, в отличие от гоев. Не будь типичным глупым гоем, "
                                           "не дай сионистам тебя провести!"))
    #    ls.append((tools.sp.get_w(""), ""))
    if any(x in text.lower() for x in why_list):
        import random
        i = random.randint(0, len(ls)-1)
        bot.send_sticker(id, ls[i][0])
        if ls[i][1] != "":
            bot.send_message(id, ls[i][1])

        return True
    return False


def why_reading_handler(message: types.Message, bot: telebot.TeleBot):
    why_reading(bot, message.from_user.id, 'ru', "зачем читать")