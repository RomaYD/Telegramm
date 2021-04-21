from telebot import types
# from telebot import types
from random import shuffle
from SQLighter import SQLighter
from config import database_name, database_name2

slovar = {}
# Считает количество строк в бд
def count_rows_musiv():
    db = SQLighter(database_name)
    rowsnum = db.count_rows()
    slovar['rows_count1'] = rowsnum
# Регистрация пользовательского имени
def set_name_from_user(NAME):
    slovar['name'] = NAME
# Использование пользовательского имени
def get_name_from_user():
    try:
        name = slovar['name']
        return name
    except KeyError:
        return None

# Считает количество строк в бд для фотографий
def count_rows_photo():
    db = SQLighter(database_name2)
    rowsnum = db.count_rows()
    slovar['rows_count2'] = rowsnum
# обращается к данным бд по строкам
def get_rows_count(type_of_cntent):
    if type_of_cntent == 'photo':
        rowsnum = slovar['rows_count2']
    elif type_of_cntent == 'music':
        rowsnum = slovar['rows_count1']
    return rowsnum

# Записывает правильный ответ по ключу - id сообщения
def set_user_game(chat_id, estimated_answer):
    slovar[str(chat_id)] = estimated_answer

# Очистка ответов
def finish_user_game(chat_id):
    del slovar[str(chat_id)]

# Получение правильного ответа
def get_answer_for_user(chat_id):
    try:
        answer = slovar[str(chat_id)]
        return answer

    except KeyError:
        return None

# Клавиатура для ответов игры
def generate_markup(right_answer, wrong_answers):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    all_answers = '{},{}'.format(right_answer, wrong_answers)
    list_items = []
    for item in all_answers.split(','):
        list_items.append(item)
    shuffle(list_items)
    for item in list_items:
        markup.add(item)
    return markup

