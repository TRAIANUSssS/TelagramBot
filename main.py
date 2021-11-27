import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
import random

token = '2101589354:AAGu2HRpEM1ynI6EMZfPTdMSl3bTp7N8kXU'

bot = telebot.TeleBot(token)
names, links, updates, lang = [], [], [], []
stickers = []
action = [False, False]


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row("Мой Git", 'Сколько я играю в игры?', 'Рулетка', "/help")
    bot.send_message(message.chat.id,
                     'Привет! Тут ты узнаешь мой гит, сколько я наиграл уже в играх, а так же сможешь сыграть в рускую рулетку',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Этот бот может показать мои проекты на гите, показать тебе сколько я играю в игры, а также ты даже сможешь сыграть в русскую рулетку!')


@bot.message_handler(commands=['back'])
def start_message(message):
    global action
    action = [False] * len(action)
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row("Мой Git", 'Сколько я играю в игры?', 'Рулетка', "/help")
    bot.send_message(message.chat.id, 'ok', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def answer(message):
    global names, links, updates, lang, action
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
    elif message.text.lower() == "рулетка" or action[0] == True or message.text.lower() == "еще раз":
        if action[0] == False or message.text.lower() == "еще раз":
            action[0] = True
            keyboard = types.ReplyKeyboardMarkup(True)
            keyboard.row('1', '2', '3', '4', '5', '6')
            keyboard.row('/back')
            bot.send_message(message.chat.id, 'Выбирай число', reply_markup=keyboard)
        else:
            num = random.randint(1, 6)
            if num == int(message.text):
                keyboard = types.ReplyKeyboardMarkup(True)
                keyboard.row('Еще раз', '/back')
                id = random.randint(1, 39)
                f = open('stickers.txt', 'r')
                line = f.readlines()
                # print(line[id])
                bot.send_sticker(message.chat.id, line[id].replace('\n', ''))
                bot.send_message(message.chat.id, 'Ты проиграл', reply_markup=keyboard)
            else:
                keyboard = types.ReplyKeyboardMarkup(True)
                keyboard.row('Еще раз', '/back')
                bot.send_message(message.chat.id, 'Ты победил', reply_markup=keyboard)
    elif message.text.lower() == "сколько я играю в игры?" or action[1] == True:
        keyboard = types.ReplyKeyboardMarkup(True)
        keyboard.row('Топ игр по наигранным часам', "Последняя активность", '/back')
        if action[1] == False:
            action[1] = True
            bot.send_message(message.chat.id, 'Что ты хочешь тут посмотреть?', reply_markup=keyboard)
        elif message.text == 'Топ игр по наигранным часам':
            line = get_all_games()
            bot.send_message(message.chat.id, line, reply_markup=keyboard)
        elif message.text == 'Последняя активность':
            line = get_last_activity()
            bot.send_message(message.chat.id, line, reply_markup=keyboard)


def get_last_activity():
    name, hours, last_activity = [], [], []
    html = requests.get('https://steamcommunity.com/id/chelovek_blin')
    soup = BeautifulSoup(html.content, 'html.parser')
    item = soup.find('div', {'class': 'profile_recentgame_header profile_leftcol_header'})
    try:
        line = item.find('h2').get_text() + ' ' + item.find('div', {
            'class': 'recentgame_quicklinks recentgame_recentplaytime'}).get_text() + '\n'
    except:
        line = 'За последние 2 недели я не играл ни в одну игру' + '\n' + 'Последние запущенные игры' + '\n'
    items = soup.find_all('div', {'class': 'recent_game_content'})
    for i in range(len(items)):
        name.append(items[i].find('a', {'class': 'whiteLink'}).get_text())
        temp = items[i].find('div', {'class': 'game_info_details'}).get_text()
        temp = temp.replace('\t', '').replace('\r', '').replace('\n', '', 1)
        hours.append(temp[:temp.find('\n'):])
        last_activity.append(temp[temp.find('\n') + 1::])
    for i in range(len(name)):
        line += name[i] + ': ' + hours[i] + ', ' + last_activity[i] + '\n'
    return line


def get_all_games():
    name = []
    hours = []
    total_hours = 0
    html = requests.get('https://steamcommunity.com/id/chelovek_blin/games/?tab=all')
    soup = BeautifulSoup(html.content, 'html.parser')
    items = soup.find('script', {'language': 'javascript'}).get_text()
    item = items[3:items.find('var rgChangingGames = [];'):]
    i = 0
    while True:
        if i < 7:
            n = item.find("name") + 7
            item = item[n::]
            name.append(item[:item.find(',') - 1:])
            n = item.find("hours_forever") + 16
            item = item[n::]
            hours.append(item[:item.find('last_played') - 3:])
            total_hours += float(hours[i].replace(',', ''))
        else:
            try:
                n = item.find("hours_forever") + 16
                item = item[n::]
                total_hours += float(item[:item.find('last_played') - 3:].replace(',', ''))
            except:
                break
        i += 1
    line = ''
    for i in range(len(name)):
        line += name[i] + ': ' + hours[i] + ' часов' + '\n'
    return 'Всего наиграно часов: ' + str(int(total_hours)) + '\n' + line


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

'''@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    global stickers
    ms = str(message)
    st = ms.find("'sticker': {'file_id': '")
    ms = ms[st:st+100:]
    ms = ms[:ms.find(',')-1:].replace("'sticker': {'file_id': '", '')
    stickers.append(ms)
    print(len(stickers))
    if len(stickers) == 40:
        print('start')
        f = open('stickers.txt', 'w')
        for i in range(40):
            f.write(stickers[i] + '\n')
        f.close()'''
