# TODO:
#   check if bot blocked by a user
#   check if a user is not active for a long time
#   manual delete of a user
#   make better file hierarchy
import telebot
from src import tools
from src.modules import reminder
from src.handlers import register_handlers
from threading import Thread


tools.init()
bot = telebot.TeleBot(tools.TOKEN, parse_mode="HTML")
register_handlers.register_all(bot)


thread = Thread(target=reminder.start, args=[bot])
thread.start()


print("Reading bot")
bot.infinity_polling(timeout=10001)
