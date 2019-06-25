import os
import redis
import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

import handler_dictionary

def handle_start_conversation(event, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)
    
    text = 'Привет! Для получения нового вопроса нажми на кнопку "Новый вопрос"'
    
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1,1000))
    
def send_message(user_id, text, vk_api):
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1,1000)) 

def handle_new_question_request(event, vk_api):
    user_id=event.user_id
    text = random.choice(list(question_dict.keys()))
    r.set(user_id, text)
    
    send_message(user_id, text, vk_api)  
    
def handle_loss(event, vk_api):
    user_id=event.user_id
    question = r.get(user_id).decode('utf8')    
    text = question_dict[question]
    
    send_message(user_id, text, vk_api)
    handle_new_question_request(event, vk_api)
    
    
def handle_solution_attempt(event, vk_api):
    user_id=event.user_id
    question = r.get(user_id).decode('utf8')
    user_message = event.text
    if question is None:
        text = 'Задайте вопрос'
    elif user_message in question_dict[question]:
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        text = 'Не правильно! Думай дальше!'
        
    send_message(user_id, text, vk_api)


if __name__ == "__main__":
    redis_host = os.environ['redis_host']
    redis_port = os.environ['redis_port']
    redis_password = os.environ['redis_password']
    redis_db = os.environ['redis_db']
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)
    
    path_to_file = os.environ['path_to_file']
    encoding_file = os.environ['encoding_file']
    question_dict = handler_dictionary.get_dict_with_questions_and_answers(path_to_file, encoding_file)
    
    vk_api_token = os.environ['vk_api_token']
    vk_session = vk_api.VkApi(token=vk_api_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Начать":
                handle_start_conversation(event, vk_api)
            elif event.text == "Новый вопрос":
                handle_new_question_request(event, vk_api)
            elif event.text == "Сдаться":
                handle_loss(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api)
