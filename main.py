import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
import random

token = '2101589354:AAGu2HRpEM1ynI6EMZfPTdMSl3bTp7N8kXU'

bot = telebot.TeleBot(token)
names, links, updates, lang = [], [], [], []
roulette = False


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row("Мой Git", 'Сколько я играю в игры?', 'Рулетка', "/help")
    bot.send_message(message.chat.id,
                     'Привет! Тут ты узнаешь мой гит, сколько я наиграл уже в играх, а так же сможешь сыграть в рускую рулетку?',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я умею...')


@bot.message_handler(commands=['back'])
def start_message(message):
    global roulette
    roulette = False
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row("Мой Git", 'Сколько я играю в игры?', 'Рулетка', "/help")
    bot.send_message(message.chat.id, 'ok', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def answer(message):
    global names, links, updates, lang, roulette
    if message.text.lower() == "мой git":
        keyboard = types.ReplyKeyboardMarkup(True)
        if len(names) == 0:
            names, links, updates, lang = get_my_projects()
        for i in range(len(names)):
            keyboard.row(types.KeyboardButton(names[i]))
        keyboard.row(types.KeyboardButton('/back'))
        bot.send_message(message.chat.id, 'Вот мои проекты на гите', reply_markup=keyboard)
    elif message.text in names:
        id = names.index(message.text)
        bot.send_message(message.chat.id, 'Это проект: ' + names[id] + '\n' + 'Язык, на котором он написан: ' + lang[
            id] + '\n' + 'Последние обновление: ' + updates[id] + '\n' + 'Ссылка на проект: ' + links[id] + '\n')
    elif message.text.lower() == "рулетка" or roulette == True or message.text.lower() == "еще раз":
        if roulette == False or message.text.lower() == "еще раз":
            roulette = True
            keyboard = types.ReplyKeyboardMarkup(True)
            keyboard.row('1', '2', '3', '4', '5', '6')
            keyboard.row('/back')
            bot.send_message(message.chat.id, 'Выбирай число', reply_markup=keyboard)
        else:
            num = random.randint(1, 1)
            if num == int(message.text):
                keyboard = types.ReplyKeyboardMarkup(True)
                keyboard.row('Еще раз', '/back')
                id = random.randint(1, 39)
                f = open('stickers.txt', 'r')
                line = f.readlines()
                print(line[id])
                bot.send_sticker(message.chat.id, line[id])
                bot.send_message(message.chat.id, 'Ты проиграл', reply_markup=keyboard)
            else:
                keyboard = types.ReplyKeyboardMarkup(True)
                keyboard.row('Еще раз', '/back')
                bot.send_message(message.chat.id, 'Ты победил', reply_markup=keyboard)


def get_my_projects():
    names = []
    links = []
    updates = []
    lang = []

    HOST = 'https://github.com'

    html = requests.get('https://github.com/TRAIANUSssS?tab=repositories')
    soup = BeautifulSoup(html.content, 'html.parser')
    items = soup.find_all('div', {'class': 'col-10 col-lg-9 d-inline-block'})
    for i in items:
        names.append(i.find('a').get_text().replace(' ', '').replace('\n', ''))
        links.append(HOST + i.find('a').get('href'))
        lang.append(i.find('span', {'itemprop': 'programmingLanguage'}).get_text())
        updates.append(i.find('relative-time', {'class': 'no-wrap'}).get_text())
    return names, links, updates, lang


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
