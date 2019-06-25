import os
import random
import redis

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove
import telegram

import handler_dictionary

SEND_QUESTION, CHECK_ANSWER = range(2)

def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Привет, я бот для викторин!', reply_markup=reply_markup)
    
    return SEND_QUESTION

def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END
    
def handle_new_question_request(bot, update):
    chat_id = update.message.chat_id
    text = random.choice(list(question_dict.keys()))
    r.set(chat_id, text)
    update.message.reply_text(text)
    
def handle_solution_attempt(bot, update):
    chat_id = update.message.chat_id
    question = r.get(chat_id).decode('utf8')
    user_message = update.message.text
    
    if question is None:
        update.message.reply_text('Ты ничего не спрашивал раньше. Задайте вопрос')
    elif user_message == 'Сдаться':
        right_answer = question_dict[question]
        update.message.reply_text(right_answer)
        handle_new_question_request(bot, update)
        return SEND_QUESTION
    
    elif user_message in question_dict[question]:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
    
    else:
        update.message.reply_text('Не правильно! Думай дальше!')   

if __name__ == '__main__':
    redis_host = os.environ['redis_host']
    redis_port = os.environ['redis_port']
    redis_password = os.environ['redis_password']
    redis_db = os.environ['redis_db']
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)
    
    path_to_file = os.environ['path_to_file']
    encoding_file = os.environ['encoding_file']
    question_dict = handler_dictionary.get_dict_with_questions_and_answers(path_to_file, encoding_file)
    
    telegram_token = os.environ['telegram_token']
    updater = Updater(telegram_token)
    
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SEND_QUESTION: [RegexHandler('Новый вопрос', handle_new_question_request)],

            CHECK_ANSWER: [MessageHandler(Filters.text, handle_solution_attempt)]
        },

        fallbacks=[CommandHandler('cancel', cancel)])
    
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
