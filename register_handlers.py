import telebot
import get_example
import base_commands_handler
import document_handler
import text_handler
import callback_handler


def register_all(bot: telebot.TeleBot):
    # commands
    bot.register_message_handler(base_commands_handler.debug, commands=["debug"], pass_bot=True)
    bot.register_message_handler(base_commands_handler.check, commands=["check"], pass_bot=True)
    bot.register_message_handler(base_commands_handler.help, commands=["help"], pass_bot=True)
    bot.register_message_handler(base_commands_handler.start, commands=["start"], pass_bot=True)
    bot.register_message_handler(base_commands_handler.swap_lang, commands=["lang"], pass_bot=True)
    bot.register_message_handler(get_example.set_example_book, commands=["example"], pass_bot=True)
    bot.register_message_handler(text_handler.why_reading_handler, commands=["why"], pass_bot=True)

    # upload a document
    bot.register_message_handler(document_handler.obtained, content_types=['document'], pass_bot=True)

    # arbitrary text handler must be invoked after all other commands,
    # otherwise commands are be ignored
    bot.register_message_handler(text_handler.process_any_text, content_types=["text"], pass_bot=True)

    # callback functions, they are needed for a response to inline buttons
    bot.register_callback_query_handler(callback_handler.callbacks, func=lambda call: True, pass_bot=True)

