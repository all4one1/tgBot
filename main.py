# TODO:
#   add examples
#   check if bot blocked
#   check if user not active for a long time
#   manual delete of a user
#   make better file hierarchy
import telebot
import reminder
import tools
import register_handlers
from threading import Thread


print("start")
tools.init()
bot = telebot.TeleBot(tools.TOKEN, parse_mode="HTML")
register_handlers.register_all(bot)


print("new thread")
thread = Thread(target=reminder.start, args=[bot])
thread.start()


print("polling")
bot.infinity_polling(timeout=10001)
