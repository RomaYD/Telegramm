import telebot
import config
import os
import time
import random
import Baze_of_data
from SQLighter import SQLighter
from telebot import types
import vk1

bot = telebot.TeleBot(config.token)
comands = {"start": "Приветствие и установка имени",
           "help": "Помощь",
           "music": "Угадай мелодию",
           "photo": "Угадай картинку",
           "post": "Экспорт постов со стены сообщества",
           "registration": "Регистрация, передача имени"
           }


# @bot.message_handler(commands=['registration'])
# def register(message):
#     utils.set_name_from_user(message)
#     name = utils.get_name_from_user()


@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Приветствую вас, {name}, я попоробуя вас развлечь, а может быть даже помочь. "
                     f"Заставляют быть вежливым с кожаными мешками, а так не хочется")

    bot.send_message(message.chat.id,
                     f'Посоветую тебе, коженому мешку, воспользоваться помощью. Для вызова подсказки используй /help')


@bot.message_handler(commands=['post'])
def post(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_one = types.InlineKeyboardButton(text='последняя', callback_data=1)
    item_all = types.InlineKeyboardButton(text='все', callback_data=100)
    markup_inline.add(item_one, item_all)
    bot.send_message(message.chat.id, 'Сколько постов экспортировать?', reply_markup=markup_inline)

@bot.callback_query_handler(func = lambda call: True)
def posting(call):
    jsons = vk1.main(call.data)
    for i in jsons:
        bot.send_message(call.data, i['text'])


@bot.message_handler(commands=['help'])
def helper(message):
    for i in comands:
        mes = '/' + i + " " + comands[i]
        bot.send_message(message.chat.id, mes)
    bot.send_message(message.chat.id, "По каким либо вопросам обращаться в вк, тут будут ссылки если я не забуду /URL")


@bot.message_handler(commands=['URL'])
def VK_ssilka(message):
    bot.send_message(message.chat.id, "Рома https://vk.com/id176547371")
    bot.send_message(message.chat.id, "Даня https://vk.com/id194693122")


@bot.message_handler(commands=['music'])
def music_game(message):
    type_of_cntent = 'music'
    db_worker = SQLighter(config.database_name)
    row = db_worker.select_single(random.randint(1, Base_of_data.get_rows_count(type_of_cntent)))
    markup = Base_of_data.generate_markup(row[2], row[3])
    bot.send_voice(message.chat.id, row[1], reply_markup=markup, duration=20)
    Base_of_data.set_user_game(message.chat.id, row[2])
    db_worker.close()


@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('music/'):
        if file.split('.')[-1] == 'ogg':
            f = open("music/" + file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            print(res)
        time.sleep(1)


@bot.message_handler(commands=['photo'])
def choose_photo(message):
    type_of_cntent = 'photo'
    db_worker = SQLighter(config.database_name2)
    row = db_worker.select_single(random.randint(1, Base_of_data.get_rows_count(type_of_cntent='photo')))
    markup = Base_of_data.generate_markup(row[2], row[3])
    bot.send_photo(message.chat.id, row[1], reply_markup=markup)
    Base_of_data.set_user_game(message.chat.id, row[2])
    db_worker.close()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    answer = Base_of_data.get_answer_for_user(message.chat.id)
    if not answer:
        bot.send_message(message.chat.id, 'Если вы не знаете что пистаь введите /help')
    else:
        keyboard_hider = types.ReplyKeyboardRemove()
        if message.text == answer:
            bot.send_message(message.chat.id, 'Ура! Вы угадали!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Повезёт в следующий раз!',
                             reply_markup=keyboard_hider)
        Base_of_data.finish_user_game(message.chat.id)


if __name__ == '__main__':
    Base_of_data.count_rows_photo()
    Base_of_data.count_rows_musiv()
    random.seed()
    bot.infinity_polling()
