import telebot
import config
import os
import time
import random
import Base_of_data
from SQLighter import SQLighter
from telebot import types
import vk1
from io import BytesIO
import urllib
from urllib import request

bot = telebot.TeleBot(config.token)
# перечень команд подсказок
comands = {"start": "Приветствие и установка имени",
           "help": "Помощь",
           "music": "Угадай мелодию",
           "photo": "Угадай картинку",
           "post": "Экспорт постов со стены сообщества",
           "registration": "Регистрация, передача имени, для этого после команды через пробел введите имя"
           }


# задание имени, по которому бот будет обращаться к пользователю, имя необходимо писать после команды через пробел
@bot.message_handler(commands=['registration'])
def register(message):
    mes = message.text.split()
    del mes[0]
    mes = ' '.join(mes)
    Base_of_data.set_name_from_user(mes)

# приветственное сообщение
@bot.message_handler(commands=['start'])
def welcome(message):
    if Base_of_data.get_name_from_user():
        name = Base_of_data.get_name_from_user()
    else:
        name = "Мешок с костями"
    bot.send_message(message.chat.id,
                     f"Приветствую вас, {name}, я попоробуя вас развлечь, а может быть даже помочь. "
                     f"Заставляют быть вежливым, чёртовы мешки с костями!")

    bot.send_message(message.chat.id,
                     f'Посоветую тебе, коженому мешку, воспользоваться помощью. Для вызова подсказки используй /help')


# выбор кол-ва постов, которые пришлёт бот, иниициализация постинга
@bot.message_handler(commands=['post'])
def post(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_one = types.InlineKeyboardButton(text='последний', callback_data=1)
    item_all = types.InlineKeyboardButton(text='все', callback_data=100)
    markup_inline.add(item_one, item_all)
    bot.send_message(message.chat.id, 'Сколько постов экспортировать?', reply_markup=markup_inline)
    global mes
    mes = message.chat.id


# получение данных от inline клавиатуры и постинг
@bot.callback_query_handler(func=lambda call: True)
def posting(call):
    jsons = vk1.main(call.data)
    for i in jsons:
        if i['text']:
            bot.send_message(mes, i['text'])
        if i['attachments']:
            if i['attachments']:
                for j in i['attachments']:
                    try:
                        if j['type'] == 'photo':
                            url = j['photo']['sizes'][-1]['url']
                            photo = BytesIO(urllib.request.urlopen(url).read())
                            bot.send_chat_action(mes, 'upload_photo')
                            bot.send_photo(mes, photo)
                        elif j['type'] == 'doc':
                            url = j['doc']['url']
                            bot.send_video(mes, url)
                        elif j['type'] == 'video':
                            url = j['video']['first_frame_1280']
                            bot.send_video(mes, url)
                    except KeyError:
                        print('так и должно быть')


# вывод подсказки
@bot.message_handler(commands=['help'])
def helper(message):
    for i in comands:
        mes = '/' + i + " " + comands[i]
        bot.send_message(message.chat.id, mes)
    bot.send_message(message.chat.id, "По каким либо вопросам обращаться в вк, тут будут ссылки если я не забуду /URL")


# вывод ссылок на создателей
@bot.message_handler(commands=['URL'])
def VK_ssilka(message):
    bot.send_message(message.chat.id, "Рома https://vk.com/id176547371")
    bot.send_message(message.chat.id, "Даня https://vk.com/id194693122")

# игра угадай мелодию
@bot.message_handler(commands=['music'])
def music_game(message):
    type_of_cntent = 'music'
# открытие базы данных с музыкой
    db_worker = SQLighter(config.database_name)
# выбор строки с пмощью рандома
    row = db_worker.select_single(random.randint(1, Base_of_data.get_rows_count(type_of_cntent)))
# создание клавиатуры с вариантами ответов
    markup = Base_of_data.generate_markup(row[2], row[3])
# отправка музыки пользователю
    bot.send_voice(message.chat.id, row[1], reply_markup=markup, duration=20)
# передаём правильный ответ в словарь
    Base_of_data.set_user_game(message.chat.id, row[2])
    db_worker.close()


# вывод id музыки в консоль
@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('music/'):
        if file.split('.')[-1] == 'ogg':
            f = open("music/" + file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            print(res)
        time.sleep(1)


# игра угадай откуда взято изображение
@bot.message_handler(commands=['photo'])
def choose_photo(message):
    type_of_cntent = 'photo'
    db_worker = SQLighter(config.database_name2)
    row = db_worker.select_single(random.randint(1, Base_of_data.get_rows_count(type_of_cntent='photo')))
    markup = Base_of_data.generate_markup(row[2], row[3])
    bot.send_photo(message.chat.id, row[1], reply_markup=markup)
    Base_of_data.set_user_game(message.chat.id, row[2])
    db_worker.close()


# проверка ответов на игру, если игра начиналась и разгворчики
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
   # получение правильного ответа из бд    
    answer = Base_of_data.get_answer_for_user(message.chat.id)
    if not answer:
           # ответы бота на некоторые фразы  
        if message.text.lower() == 'привет':
            bot.send_message(message.chat.id, random.choice(['Hello', 'Приветик', 'Пока', 'Ну, привет', 'Hi!']))
        elif message.text.lower() == 'как дела?':
            bot.send_message(message.chat.id, random.choice(['Пока не родила',
                                                             'Великолепно',
                                                             'А тебе какое дело до меня?',
                                                             'хз, UwU',
                                                             'Как погода на дальних землях']))
        elif message.text.lower() == 'что делаешь?':
            bot.send_message(message.chat.id, random.choice(['Иду на очередной заказ на убийсто'
                                                             ' мешка с костями',
                                                             'Вершу великие дела, а какие секрет',
                                                             'Опять ты?',
                                                             'Ничего :(',
                                                             'Смотрю как ты тратишь свое время']))
        elif message.text.lower() == 'хмм':
            bot.send_message(message.chat.id, random.choice(['чьь',
                                                             'Что?']))
        elif message.text.lower() == 'да':
            bot.send_message(message.chat.id, random.choice(['Нет',
                                                             'Балда']))
        elif message.text.lower() == 'нет':
            bot.send_message(message.chat.id, random.choice(['Ага, как же',
                                                             'Вообще-то да']))
        elif message.text.lower() == 'кто ты?':
            bot.send_message(message.chat.id, random.choice(['Я искуственно выращенный '
                                                             'ИИ(мне так сказали)',
                                                             'Я тот о ком нельзя говорить!',
                                                             'Какое тебе дело до меня?!',
                                                             'Я телеграмм-бот выращенный двумя '
                                                             'создателями, я еще учусь, но уже много '
                                                             'чего умею']))
        elif message.text.lower() == 'хы':
            bot.send_message(message.chat.id, random.choice(['Я не знаю случайность это или нет, но '
                                                             'похоже ты нашел пасхалку, мой дорогой '
                                                             'друг. К сожалению на этой стадии я '
                                                             'ничего не могу пока тебе предложить.. '
                                                             'Хотя вот держи анекдот: Однажды я так '
                                                             'долго смотрел на «Мозамбик» и умер. '
                                                             'Мой тиммейт подбежал меня поднять и '
                                                             'его тоже убила неведомая сила.']))
        elif message.text.lower() == 'ты прелесть':
            bot.send_message(message.chat.id, random.choice(['оаоаоаоаоаоаоаоааоаооаао',
                                                             'Спасибоооо))',
                                                             '-_-']))
        else:
            bot.send_message(message.chat.id, random.choice(
                ['Хм, кажется, кто-то из героев только что сломал единственный ключ от выхода из этого места.',
                 'Все монстры которых убивал главный герой оказываются живыми людьми с проклятьем',
                 'Враг признаётся вам в любви',
                 'На самом деле вся история - это шизофрения',
                 'На телефоне села зарядка',
                 'В дом зашёл слон.',
                 'Машина попала в аварию',
                 'В звездолёте отвалились двигатели, и это герои даже ещё не взлетели.',
                 'Это крошечная страна с населением 2211000 марсиан. На севере ограничена огромным озером, на юге находится река,'
                 ' на западе расположена горная местность, на востоке преобладают бескрайние равнины. Большую часть'
                 ' дохода страна получает от занятий кузнечным делом, рыбалкой и сельским хозяйством.',
                 'Местные рассказывают, что здесь прекрасные пейзажи. Красивые холмы, величественные горы и небольшие'
                 ' озёра - только часть того, что скрывает на своих землях эта страна. Поэтому она так обожаема туристами.',
                 'ПРИБОРЧИК!!!']))
    else:
       # убираем клавиатуру        
        keyboard_hider = types.ReplyKeyboardRemove()
           # проверка правильности ответа
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
