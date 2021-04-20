import telebot
import time
import config
import os

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('music/'):
        if file.split('.')[-1] == 'ogg':
            f = open('music/'+file, 'rb')
            msg = bot.send_voice(message.chat.id, f, None)
            bot.send_message(message.chat.id, msg.voice.file_id, reply_to_message_id=msg.message_id)
        time.sleep(1)

@bot.message_handler(commands=['test1'])
def find_file_ids(message):
    for file in os.listdir('photo/'):
        if file.split('.')[-1] == 'jpg':
            f = open('photo/'+file, 'rb')
            msg = bot.send_photo(message.chat.id, f, None)
            bot.send_message(message.chat.id, msg.photo[-1].file_id, reply_to_message_id=msg.message_id)
        time.sleep(3)


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=123)