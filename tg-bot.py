from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove
import telegram
import os
import random
import redis

import handler_dictionary

SEND_QUESTION, SURRENDER, CHECK_ANSWER = range(3)

def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Привет, я бот для викторин!', reply_markup=reply_markup)
    
    return SEND_QUESTION

def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
    
def handle_loss(bot, update):
    chat_id = update.message.chat_id
    question = r.get(chat_id).decode('utf8')   
    text = question_dict[question]
    right_answer = question_dict[question]
    update.message.reply_text(right_answer)
    handle_new_question_request(bot, update)
    
    
def handle_new_question_request(bot, update):
    chat_id = update.message.chat_id
    text = random.choice(list(question_dict.keys()))
    r.set(chat_id, text)
    update.message.reply_text(text)
    
    return CHECK_ANSWER
    
def handle_solution_attempt(bot, update):
    chat_id = update.message.chat_id
    question = r.get(chat_id).decode('utf8')
    user_message = update.message.text
    if question is None:
        update.message.reply_text('Задайте вопрос')
    elif user_message == 'Сдаться':
        right_answer = question_dict[question]
        update.message.reply_text(right_answer)
        handle_new_question_request(bot, update)
        
    elif user_message in question_dict[question]:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        return SEND_QUESTION
    
    else:
        update.message.reply_text('Не правильно! Думай дальше!')   

if __name__ == '__main__':
    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']
    redis_db = os.environ['REDIS_DB']
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)
    
    path_to_file = os.environ['PATH_TO_FILE']
    file_encoding = os.environ['FILE_ENCODING']
    question_dict = handler_dictionary.get_dict_with_questions_and_answers(path_to_file, file_encoding)
    
    telegram_token = os.environ['TELEGRAM_TOKEN']
    updater = Updater(telegram_token)
    
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SEND_QUESTION: [RegexHandler('^Новый вопрос$', handle_new_question_request)],
            
            SURRENDER: [RegexHandler('^Сдаться$', handle_loss, r)],

            CHECK_ANSWER: 
            [RegexHandler('^Новый вопрос$', handle_new_question_request),
                MessageHandler(Filters.text, handle_solution_attempt, r)]
        },

        fallbacks=[CommandHandler('cancel', cancel)])
    
    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

