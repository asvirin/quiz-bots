import re
import os

def get_dict_with_questions_and_answers(path, encoding):
    question_dict = {}
    file = os.path.dirname(path)
    file_with_information = open(file, "r", encoding=encoding).read().split('\n\n\n')
    for part in file_with_information:
        question_with_answer = part.split('\n\n')
        for text in question_with_answer:
            if 'Вопрос' in text:
                question = re.split(r':', text ,maxsplit=1)
                text_question = question[1].replace('\n', '')
            if 'Ответ' in text:
                answer = re.split(r':', text ,maxsplit=1)
                text_answer = answer[1].replace('\n', '')
        question_dict[text_question] = text_answer    
    
    return question_dict
